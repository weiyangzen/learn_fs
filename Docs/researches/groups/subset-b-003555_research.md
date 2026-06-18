# subset-b-003555 Research

Work item: subset-b-003555

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-sn65dsi86.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-sn65dsi86.c

Purpose: implements the Texas Instruments SN65DSI86 MIPI DSI to eDP/DisplayPort bridge as a multi-function I2C driver. The top-level I2C device owns power, regulators, regmap, runtime PM, IRQ, and shared state, then exposes auxiliary child devices for DP AUX, DRM bridge, GPIO controller, and PWM controller so probe ordering can satisfy panels/backlights that depend on bridge-provided resources.

Important APIs/types/functions: `struct ti_sn65dsi86` is the shared device state: bridge/AUX/gpio/pwm auxiliary devices, `drm_dp_aux`, `drm_bridge`, MIPI DSI attachment, refclk, regulators, lane assignment/polarity, runtime communication flags, HPD flags, GPIO output bitmap, PWM pin ownership, and PWM refclk cache. Regmap helpers wrap 8-bit and 16-bit register access. `ti_sn65dsi86_resume()` enables supplies and EN GPIO, waits for reference-clock latch, optionally enables communications, and arms IRQs; `ti_sn65dsi86_suspend()` disables comms, EN, and regulators. The DP AUX implementation is `ti_sn_aux_transfer()`, with DPCD/I2C-over-AUX request translation, address/length programming, status clearing, SEND polling, short-reply handling, and NACK mapping. Bridge hooks include `ti_sn_bridge_attach()`, `mode_valid()`, `atomic_pre_enable()`, `atomic_enable()`, `atomic_disable()`, `atomic_post_disable()`, `detect()`, `edid_read()`, HPD enable/disable, and debugfs status. Optional PWM and GPIO blocks register `pwm_chip` and `gpio_chip` subdevices.

Control flow: probe validates I2C support, allocates the bridge object, initializes regmap and PM, powers the chip long enough to read the backwards ID string, requests threaded IRQ if present, and creates gpio/pwm/aux auxiliary devices. AUX probe initializes the DP AUX adapter, populates DP AUX endpoint devices, then adds the bridge auxiliary device. Bridge probe locates the downstream panel/bridge, parses DP lane mapping and polarity from graph endpoint data, finds the upstream DSI host, sets eDP versus DisplayPort type, optionally updates HPD disable state, adds the DRM bridge, and attaches the MIPI DSI device. Enable flow powers runtime PM, enables comms if no standalone refclk exists, programs DSI rate/lane mapping/output format/ASSR or scrambler mode, reads sink-supported DP rates, trains from the minimum viable DP rate upward, writes timing registers, and enables the video stream. Disable flow disables stream, link training, lanes, PLL, comms, and runtime PM.

State and persistence: persistent driver state is mainly `comms_enabled`, `hpd_enabled`, `dp_lanes`, lane remap fields, PWM/GPIO pin ownership, `gchip_output`, and `pwm_enabled`; hardware state is volatile because regcache is disabled and the bridge loses register programming across powerdown. Runtime PM references are used as persistence guards: GPIO outputs and active PWM keep the chip powered, while inputs are allowed to reset to default input state. `pwm_refclk_freq` mirrors the DPPLL refclk register choice because PWM math depends on that encoded value rather than the physical clock source.

Dependencies and integration points: depends on Linux I2C, regmap, regulator, GPIO, clk, runtime PM, auxiliary bus, PWM, OF graph, MIPI DSI, DRM bridge, bridge connector, DP AUX/DDC/DPCD helpers, EDID helpers, and optional DP AUX endpoint devices. It integrates with panels through downstream bridge lookup, with the upstream host through `devm_mipi_dsi_device_register_full()`/attach, with userspace through DRM connector/HPD/EDID, debugfs `status`, PWM, and GPIO controller APIs.

Risks: many register writes ignore return values, so transient I2C failures can leave partial hardware state. `ti_sn_attach_host()` hardcodes four DSI lanes and RGB888 regardless of DT. DP lane count is clamped after reading the sink, mutating the parsed DT lane count. AUX cannot work before pre-enable on no-refclk boards. PWM updates are intentionally non-atomic across period/duty registers, and GPIO/PWM share GPIO4 through an atomic busy flag that must remain coherent with runtime PM. Link training failure only disables PLL; earlier DSI/video configuration remains until post-disable. HPD behavior differs for eDP and DisplayPort and depends on bridge type being set before communications are enabled.

Test signals: compile with and without `CONFIG_OF_GPIO` and `CONFIG_PWM`; probe on boards with refclk and DSI-derived refclk; EDID read before/after pre-enable; eDP ASSR and external DisplayPort scrambler-disable cases; DP rate fallback for eDP 1.1 and custom eDP 1.4 rate tables; HPD IRQ insertion/removal; runtime suspend/resume while PWM or GPIO output is active; GPIO4 contention between PWM and GPIO; link-training retry/failure logs; debugfs status reads; and mode validation for porch/pulse width register limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-sn65dsi86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tdp158.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tdp158.c

Purpose: provides a small DRM bridge driver for the TI TDP158 HDMI/DVI retimer/redriver. It models the chip as an I2C device that powers two regulators and an optional operation-enable GPIO around bridge enable/disable, then passes attach through to the next bridge.

Important APIs/types/functions: `struct tdp158` stores the embedded `drm_bridge`, downstream bridge, enable GPIO, `vcc` and `vdd` regulators, and device pointer. `tdp158_probe()` allocates the bridge with `devm_drm_bridge_alloc()`, gets the downstream bridge from OF graph port 1, obtains `vcc` and `vdd` regulators, gets optional `enable` GPIO initialized low, fills `bridge.of_node` and `driver_private`, and registers with `devm_drm_bridge_add()`. `tdp158_attach()` delegates to `drm_bridge_attach()`. `tdp158_enable()` enables `vcc`, enables `vdd`, and asserts enable; `tdp158_disable()` deasserts enable and disables regulators in reverse order.

Control flow: the bridge has no mode validation, format negotiation, HPD, EDID, or runtime PM. It relies on its position in the bridge chain and the downstream bridge for connector behavior. Atomic enable/disable are the only runtime hooks.

State and persistence: there is no explicit software state beyond devm-managed pointers. Hardware state is the regulator and enable GPIO levels. Failed regulator enables are logged but do not abort the enable callback or roll back the other rail.

Dependencies and integration points: depends on DRM bridge atomic helper state allocation, OF graph bridge lookup, regulator framework, GPIO consumer API, and I2C driver matching via `ti,tdp158`. It integrates into display pipelines as a transparent bridge that must be powered when the upstream encoder drives TMDS.

Risks: ignored regulator errors can leave the enable GPIO asserted with one rail missing. Disable unconditionally calls `regulator_disable()` even if enable failed partially. No timing delays are implemented around regulator and enable sequencing, so board-specific requirements must be satisfied externally or by regulator/GPIO constraints.

Test signals: device-tree graph probe/defer, regulator failure injection, enable/disable sequencing on suspend and modeset, bridge-chain attach with downstream bridge, and checking that the optional enable GPIO being absent is tolerated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tdp158.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tfp410.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tfp410.c

Purpose: implements the TI TFP410 parallel RGB to DVI transmitter as a DRM bridge, supporting both platform and I2C instantiation. The driver wraps a downstream bridge/connector, controls an optional powerdown GPIO, reports input bus format/timing constraints, handles fallback connector creation, and debounces HPD callbacks from the next bridge.

Important APIs/types/functions: `struct tfp410` holds `drm_bridge`, optional local `drm_connector`, negotiated `bus_format`, delayed HPD work, powerdown GPIO, bridge timings, and device pointer. `tfp410_parse_timings()` sets default timings or parses non-I2C strap-mode endpoint properties (`pclk-sample`, `bus-width`) plus `ti,deskew` to derive input bus flags, setup/hold time, and RGB888 24-bit or 2x12 media-bus format. `tfp410_attach()` attaches the downstream bridge with `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, optionally initializes a connector when caller did not request no-connector, wires DDC from the next bridge, sets polling based on downstream detect/HPD ops, and enables debounced HPD. `tfp410_get_modes()` reads EDID from the next bridge if available and otherwise adds no-EDID modes up to 1920x1200 with 1024x768 preferred. `tfp410_get_input_bus_fmts()` and `tfp410_atomic_check()` advertise the configured input format and bus flags.

Control flow: `tfp410_init()` validates OF data, allocates the bridge, parses timings, finds the next bridge at graph port 1, gets an optional `powerdown` GPIO initially high, and registers the bridge. Platform probe calls `tfp410_init(..., false)`, while I2C probe validates the `reg` property and calls `tfp410_init(..., true)`. Module init attempts I2C registration when enabled, then platform registration, and succeeds if at least one registration worked.

State and persistence: persistent state is static configuration parsed from DT and the delayed HPD work item. Runtime hardware state is only the powerdown GPIO. The driver does not program TFP410 registers in I2C mode; it assumes default I2C-mode strap behavior.

Dependencies and integration points: depends on DRM bridge/connector helpers, EDID helpers, OF graph, media bus formats, GPIO consumer API, workqueues, platform and optional I2C driver infrastructure. Downstream bridge ops provide EDID, detect, HPD, DDC, and connector type.

Risks: I2C mode is nominal only; no I2C configuration is implemented. If connector initialization fails after downstream HPD was enabled, the current attach path returns without disabling HPD work. The connector is created only when the upstream did not request no-connector, so modern bridge-connector pipelines usually bypass local connector logic. Bad DT timing fields return `-EINVAL` and prevent probe.

Test signals: platform and I2C probe paths, 12-bit and 24-bit bus format negotiation, deskew boundary values 0..7, powerdown GPIO polarity, EDID and fallback no-EDID modes, HPD debounce and detach cancellation, and 25 MHz to 165 MHz mode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tfp410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tpd12s015.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tpd12s015.c

Purpose: models the TI TPD12S015 HDMI ESD protection and level-shifter chip as a DRM bridge. It controls cable-power/HPD and level-shifter output-enable GPIOs, reports HDMI-A hotplug status from an HPD GPIO, and forwards bridge attachment to the downstream bridge.

Important APIs/types/functions: `struct tpd12s015_device` contains the embedded bridge, `ct_cp_hpd_gpio`, `ls_oe_gpio`, required `hpd_gpio`, and optional IRQ number. `tpd12s015_probe()` allocates the bridge, sets type `DRM_MODE_CONNECTOR_HDMIA` and detect op, finds the next bridge from graph port 1, obtains three GPIOs by index, optionally requests a threaded HPD IRQ on rising/falling edges, sets `DRM_BRIDGE_OP_HPD` when IRQ registration succeeds, and calls `drm_bridge_add()`. `tpd12s015_attach()` requires `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, attaches the next bridge, asserts level-shifter output enable, and waits 300 to 1000 us for the DC-DC converter. `tpd12s015_detach()` disables the level shifter. `tpd12s015_hpd_enable()`/disable toggle `ct_cp_hpd_gpio`, and `tpd12s015_hpd_isr()` calls `drm_bridge_hpd_notify()`.

Control flow: the bridge is intended to sit inside a bridge chain where a bridge connector owns the connector. Detection directly reads HPD GPIO. HPD notification is optional and only active when the HPD GPIO can be converted to an IRQ.

State and persistence: no separate software state is stored beyond GPIO descriptors and IRQ number. Hardware state is the GPIO levels. Attach leaves `ls_oe_gpio` asserted until detach, while HPD enable/disable toggles the HPD/cable-power control line.

Dependencies and integration points: depends on platform driver infrastructure, OF graph, GPIO consumer API, IRQ handling, and DRM bridge HPD/detect hooks. It integrates with downstream HDMI bridge/encoder chains and bridge connector polling/HPD logic.

Risks: attach returns `-EINVAL` if a connector-creating caller is used. GPIOs are positional and unnamed, so DT ordering is critical. There is no explicit remove-time detach of GPIO state beyond `drm_bridge_remove()`, so normal DRM detach sequencing must run. HPD IRQ absence leaves only polled detect behavior.

Test signals: graph probe/defer, three-GPIO DT ordering and polarity, attach with no-connector flag, HPD GPIO read for connected/disconnected states, IRQ-triggered HPD notify on both edges, and output-enable timing during bridge attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tpd12s015.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/waveshare-dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/waveshare-dsi.c

Purpose: implements a Waveshare DSI-to-DPI bridge as an I2C-controlled DRM bridge with an internal raw backlight device. It creates and attaches a MIPI DSI device to the upstream DSI host, wraps the downstream panel as a panel bridge, and writes simple control registers for bridge and backlight enable/brightness.

Important APIs/types/functions: `struct ws_bridge` holds the DRM bridge, next bridge, backlight, device, and I2C regmap. `ws_bridge_attach_dsi()` finds the DSI host from graph port 0, registers a `mipi_dsi_device`, sets video HSE/video/non-continuous clock flags and RGB888 format, reads data-lane count from endpoint with fallback to two lanes, and attaches the DSI device. `ws_bridge_probe()` allocates state, initializes regmap, finds the downstream panel at graph port 1, creates a panel bridge, registers a raw backlight, writes initial control registers `0xc0`, `0xc2`, and `0xac`, registers the DRM bridge, then attaches DSI. Bridge hooks attach the next bridge, enable by writing `0xad=1` and enabling backlight, and disable by disabling backlight then writing `0xad=0`. Backlight update writes inverted brightness to `0xab` and commits with `0xaa=1`.

Control flow: probe must find both DSI host and panel through the OF graph. Runtime bridge enable/disable only toggles the bridge output and backlight; there are no mode validation, bus format, HPD, or EDID callbacks.

State and persistence: state is the regmap-backed bridge registers and kernel backlight brightness. Register settings are not cached by regmap and no runtime PM is used, so suspend/resume persistence depends on parent I2C device behavior and panel/bridge sequencing.

Dependencies and integration points: depends on I2C/regmap, DRM bridge and panel bridge helpers, MIPI DSI, OF graph, and backlight core. Compatible string is `waveshare,dsi2dpi`.

Risks: register semantics are magic constants with no local definitions. I2C write errors in enable/disable/backlight update are ignored. DSI lane fallback preserves old DT behavior but can hide invalid descriptions. No remove callback is needed because devm is used, but the attached DSI device and bridge state depend on devm cleanup order.

Test signals: DSI host probe deferral, panel bridge creation, lane count 1..4 and fallback path, backlight brightness inversion, enable/disable I2C writes on scope or register trace, and suspend/resume if the chip loses register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/waveshare-dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build-igt.sh -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build-igt.sh

Purpose: builds a pinned IGT GPU Tools tree inside the DRM CI container, installs it under `/igt`, generates a flattened CI test list including subtests, packages the result, and uploads it to MinIO/S3 for later test jobs.

Important APIs/functions: `generate_testlist()` reads IGT's `test-list.txt`, skips sentinel lines, runs each test binary with `--list-subtests`, and writes either plain test names or `test@subtest` entries to `/igt/libexec/igt-gpu-tools/ci-testlist.txt`. The main script clones `https://gitlab.freedesktop.org/drm/igt-gpu-tools.git`, checks out `$IGT_VERSION`, optionally creates an armhf Meson cross file for `KERNEL_ARCH=arm`, sets Meson options for disabled overlay/chamelium/valgrind and enabled tests/runner/man/libunwind, disables the xe driver on ARM/ARM64, builds with Ninja, installs to `/igt`, sets architecture-specific `LD_LIBRARY_PATH`, tars/gzips `/igt`, and uploads `igt.tar.gz` using `ci-fairy s3cp`.

Control flow: `set -ex` makes each command visible and aborts on failure except `--list-subtests`, where failures produce plain test entries. Ninja retries serially if the parallel build fails.

State and persistence: writes the clone, build directory, `/igt`, generated test list, `artifacts/igt.tar`, and uploaded S3 object at `${PIPELINE_ARTIFACTS_BASE}/${KERNEL_ARCH}/igt.tar.gz`.

Dependencies and integration points: depends on Git, Meson, Ninja, IGT build dependencies from the container image, optional Mesa CI cross-file helper, `FDO_CI_CONCURRENT`, `KERNEL_ARCH`, `IGT_VERSION`, `S3_JWT_FILE`, and `PIPELINE_ARTIFACTS_BASE`. Consumed by `igt_runner.sh` in LAVA/crosvm tests.

Risks: network clone and checkout are live external dependencies. `generate_testlist()` executes every IGT test binary in listing mode, so missing runtime libraries or broken binaries can silently collapse to whole-test entries. Upload path must match test runner architecture mapping. `tar -cf artifacts/igt.tar /igt` uses an absolute path and extraction later expects that layout.

Test signals: successful IGT checkout at the pinned SHA, Meson config for all three architectures, generated `ci-testlist.txt` containing subtests, S3 upload presence, and downstream runner extraction of `/igt`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build-igt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build.sh -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build.sh

Purpose: builds DRM CI kernels for x86_64, arm64, and arm, packages kernel images, selected DTBs, modules, CI scripts, and configuration artifacts, and optionally uploads test-stage files to MinIO.

Important APIs/functions: after sourcing Mesa CI `container_pre_build.sh`, the script installs `libssl-dev` and `python3-lxml`, chooses `GCC_ARCH`, Debian arch, kernel image name behavior, and a curated DTB list based on `$KERNEL_ARCH`, exports `ARCH` and `CROSS_COMPILE`, creates `ld-links` symlinks to force BFD ld, configures Git identity, removes stale rebase directories, merges optional `*-external-fixes` branches from upstream/origin/MR target, creates `.config` via `merge_config.sh` or `make $(basename DEFCONFIG)`, applies `ENABLE_KCONFIGS` and `DISABLE_KCONFIGS` with `scripts/config`, builds kernel image(s), DTBs, modules, and module install tree, copies CI support files into `install`, sources `container_post_build.sh`, optionally uploads kernel files and `kernel-files.tar.zst`, then creates `artifacts/install.tar` plus `.config`.

Control flow: architecture branches define toolchain and DTB coverage. Upload branch is gated by `UPLOAD_TO_MINIO=1`. The script builds modules even for build-only jobs so test artifacts have loadable modules.

State and persistence: mutates git working tree by pulling external fixes, writes `.config`, kernel build outputs, `/kernel`, `install/`, `artifacts/`, and S3 objects. The final GitLab artifact is `artifacts/install.tar`, containing CI scripts, modules, images, and common test helpers.

Dependencies and integration points: depends on freedesktop/Mesa CI container helpers, Debian packages, kernel build system, cross compilers, GitLab variables (`UPSTREAM_REPO`, `TARGET_BRANCH`, MR vars), MinIO token variables, and `drivers/gpu/drm/ci/*` scripts. Feeds `testing:*`, LAVA, crosvm, dtbs, and KUnit jobs.

Risks: external-fixes pulls can change the tree under test and introduce merge failures. Device-tree lists are manually curated and can drift with kernel path renames. `apt-get` inside jobs adds mutable package dependencies. Some command substitutions use unquoted variables. Build failures may be obscured by large logs unless artifacts are preserved.

Test signals: artifact tar contains expected images/modules/scripts for each arch, DTBs exist for configured paths, external-fixes merge behavior on MR and non-MR pipelines, MinIO upload URLs, module install layout, and `.config` includes requested enable/disable fragments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build.yml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build.yml

Purpose: defines GitLab CI build templates and concrete jobs for DRM kernel builds and IGT builds across arm32, arm64, and x86_64, plus disables unrelated inherited Mesa build jobs.

Important jobs/templates: `.build` runs `drivers/gpu/drm/ci/build.sh` in the `build-only` stage and publishes `artifacts`. `.build:arm32`, `.build:arm64`, and `.build:x86_64` layer architecture-specific containers, runner tags, `DEFCONFIG`, `KERNEL_IMAGE_NAME`, and `KERNEL_ARCH`. `igt:arm32`, `igt:arm64`, and `igt:x86_64` reuse those architecture templates but run `build-igt.sh`. `testing:*` jobs build kernels for hardware tests, enable lockdep/debug Kconfig options, set `UPLOAD_TO_MINIO=1`, and select architecture merge fragments. `build-nodebugfs:arm64` exercises a DEBUG_FS-disabled configuration with MSM XML validation.

Control flow: jobs extend shared `.build-rules` from `gitlab-ci.yml`, so scheduling depends on MR, merge, scheduled, direct-push, and fork conditions. The many inherited Mesa jobs are disabled with `rules: when: never` to keep this kernel CI focused.

State and persistence: produces GitLab artifacts and, for `testing:*`, MinIO artifacts consumed by test jobs. No direct source state changes are made in YAML, but variables configure `build.sh` behavior.

Dependencies and integration points: depends on included Mesa/freedesktop templates for `.use-debian/*` images and runner tags, and on local scripts `build.sh` and `build-igt.sh`. `test.yml`, `check-devicetrees.yml`, and KUnit jobs depend on the build templates and artifacts.

Risks: template names inherited from Mesa CI are external contract points. Disabled jobs must track upstream Mesa job renames or new inherited jobs may appear unexpectedly. Build variables must remain synchronized with architecture handling in `build.sh`.

Test signals: GitLab pipeline expands expected `build:*`, `testing:*`, and `igt:*` jobs; disabled inherited jobs remain skipped; artifacts are available to declared consumers; and `testing:*` jobs upload MinIO objects for LAVA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/check-devicetrees.yml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/check-devicetrees.yml

Purpose: adds GitLab CI jobs for device-tree binding and DTB schema checks scoped to display/GPU schemas.

Important jobs/templates: `.dt-check-base` runs in `static-checks`, sets `GIT_DEPTH=1`, enables GitLab's new bash eval strategy, sets default `SCHEMA=display:gpu`, creates a venv at `/tmp/dtcheck-venv`, installs clang/lld/llvm for `$LLVM_VERSION`, Python venv/pip, yamllint, and `dtschema`, then runs `drivers/gpu/drm/ci/${SCRIPT_NAME}`. It preserves `${ARTIFACT_FILE}` on failure and allows exit code 102 for warnings. `dtbs-check:arm32` and `dtbs-check:arm64` extend architecture build templates and run `dtbs-check.sh`. `dt-binding-check` extends the x86_64 build container and runs `dt-binding-check.sh`.

Control flow: the shell scripts produce normal failure exit 1 for make errors and exit 102 when stderr log files are non-empty, so schema warnings can be soft failures.

State and persistence: creates a per-job Python virtual environment, log files `dtbs-check.log` or `dt-binding-check.log`, and failure artifacts.

Dependencies and integration points: depends on `.build:*` templates, Debian packages, kernel DT build targets, the `dtschema` Python package, `setup-llvm-links.sh`, and environment variables `KERNEL_ARCH`, `LLVM_VERSION`, `SCRIPT_NAME`, and `ARTIFACT_FILE`.

Risks: `pip install dtschema` is not pinned, so schema tooling can change independently. `SCHEMA=display:gpu` narrows coverage and may miss non-display dependencies. Exit code 102 being allowed must remain aligned with GitLab and script behavior.

Test signals: job expansion for arm32/arm64 binding checks, venv activation, successful `make dt_binding_check`/`dtbs_check`, warning-only jobs marked allowed failure, and log artifacts on warnings or failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/check-devicetrees.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/check-patch.py -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/check-patch.py

Purpose: runs Linux `scripts/checkpatch.pl` over all commits in a merge request branch relative to the merge target common ancestor.

Important APIs/functions: the script builds a remote URL from `CI_MERGE_REQUEST_PROJECT_PATH`, sets `GIT_DEPTH=1000`, removes any stale `check-patch` remote, adds and fetches the merge target branch, computes `merge-base` against `HEAD`, removes the temporary remote, checks whether there are commits after the ancestor, and runs `scripts/checkpatch.pl --terse --types $CHECKPATCH_TYPES --git ancestor...`.

Control flow: subprocess `check_call()` aborts on Git failures. Empty commit range exits success. Nonzero checkpatch return prints a failure message and exits 1.

State and persistence: mutates local Git remotes temporarily and fetches target history. No files are written except normal Git remote metadata.

Dependencies and integration points: depends on Git, Python 3, CI MR variables, Linux `scripts/checkpatch.pl`, and `CHECKPATCH_TYPES` from `static-checks.yml`. It is intended only for merge_request_event pipelines.

Risks: assumes CI variables exist; running outside MR context raises `KeyError`. A shallow depth of 1000 can still fail for very old branches. The `errors` variable is unused. The output includes a non-ASCII failure mark, which is harmless for CI logs but notable for plain-console consumers.

Test signals: MR pipeline with target branch fetch, empty branch skip, branch with checkpatch failures, remote cleanup after run, and behavior when the common ancestor lies beyond fetched depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/check-patch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/container.yml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/container.yml

Purpose: customizes inherited freedesktop/Mesa container jobs for DRM CI by pointing ci-templates at the DRM CI project cache and specifying extra Debian packages for build and test images while disabling unused inherited containers.

Important sections: `.container` overrides `CI_REPOSITORY_URL` and `CI_COMMIT_SHA` so container templates clone the pinned `DRM_CI_PROJECT_URL`/`DRM_CI_COMMIT_SHA`. `debian/x86_64_build-base` adds kernel/IGT build dependencies such as cairo, elfutils, kmod, pciaccess, proc2, udev, unwind, docutils, bc, ply, and OpenSSL. `debian/arm64_build` adds crossbuild and armhf library variants for arm builds. `debian/*_test-gl` add runtime libraries and `jq` needed by IGT/deqp runner environments. Most other inherited container targets are disabled with `rules: when: never`.

Control flow: this file is data consumed by GitLab's include/extends engine; jobs are built only if selected by rules in `gitlab-ci.yml`.

State and persistence: affects container images tagged through `image-tags.yml`, with no runtime file writes itself.

Dependencies and integration points: depends on freedesktop ci-templates naming conventions and Mesa CI's container hierarchy. Build/test jobs in `build.yml`, `kunit.yml`, and `test.yml` extend these images.

Risks: package names are Debian-release sensitive (`t64` runtime names in test images). The arm64 build image includes armhf cross packages and must stay aligned with `build-igt.sh` arm cross file. Disabled inherited jobs can become stale if upstream template job names change.

Test signals: container pipelines expand only intended Debian build/test images; packages resolve in current Debian base; image tags are short enough for sanity checks; and downstream jobs find required libraries at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/container.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/dt-binding-check.sh -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/dt-binding-check.sh

Purpose: runs the kernel `dt_binding_check` target for DRM CI with a configurable schema filter and treats warnings as a distinct soft-failure status.

Important behavior: the script uses `set -euxo pipefail`, activates `${VENV_PATH:-/tmp/dtschema-venv}`, runs `make -j${FDO_CI_CONCURRENT:-4} dt_binding_check DT_SCHEMA_FILES="${SCHEMA:-}"` with stderr redirected to `dt-binding-check.log`, exits 1 on make failure, and exits 102 if the log file is non-empty after a successful make.

Control flow: all setup is expected to be done by `check-devicetrees.yml`; this script only activates the venv and runs make. Exit 102 is intentionally allowed by CI for warning-only reports.

State and persistence: writes `dt-binding-check.log`, which becomes a failure artifact.

Dependencies and integration points: depends on a Python venv containing `dtschema`, kernel make targets, `FDO_CI_CONCURRENT`, and optional `SCHEMA`. Used by the `dt-binding-check` GitLab job.

Risks: any stderr output, even benign make noise, is treated as warnings and exit 102. If the venv path is wrong, `source` fails immediately. No LLVM setup is done here because binding checks normally do not need the compiler symlink helper.

Test signals: successful empty-log binding check, warning log causing exit 102, make failure causing exit 1, and schema filtering through `SCHEMA=display:gpu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/dt-binding-check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/dtbs-check.sh -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/dtbs-check.sh

Purpose: runs architecture-specific `dtbs_check` under LLVM for DRM CI and reports schema warnings through a special allowed-failure exit code.

Important behavior: the script requires `KERNEL_ARCH` and `LLVM_VERSION`, calls `setup-llvm-links.sh`, runs `make LLVM=1 ARCH="$KERNEL_ARCH" defconfig`, then runs parallel `make ARCH="$KERNEL_ARCH" LLVM=1 dtbs_check DT_SCHEMA_FILES="${SCHEMA:-}"` with stderr redirected to `dtbs-check.log`. It exits 1 on make failure and 102 if the warning log is non-empty.

Control flow: setup is strict through `set -euxo pipefail` and parameter expansion guards. A clean `dtbs_check` with empty stderr exits 0.

State and persistence: writes `.config` and build artifacts through kernel make, plus `dtbs-check.log` for CI artifact collection.

Dependencies and integration points: depends on LLVM packages and symlinks, kernel DT build system, `dtschema` venv from the GitLab before_script, and the architecture variables supplied by `check-devicetrees.yml`.

Risks: `defconfig` is used rather than DRM CI's testing config, so check coverage follows architecture defaults. As with binding checks, any stderr output is treated as a warning. LLVM version symlink creation writes into `/usr/bin` and assumes job container privileges.

Test signals: arm32/arm64 execution, `setup-llvm-links.sh` success, warning-only exit 102, hard make failure exit 1, and schema filter honoring `SCHEMA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/dtbs-check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/gitlab-ci.yml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/gitlab-ci.yml

Purpose: is the top-level GitLab CI configuration for DRM kernel CI. It pins the external Mesa/DRM CI environment, includes freedesktop and Mesa templates, defines pipeline-wide variables, stages, rule anchors, build/container scheduling policy, sanity checks, archive generation, and imports local CI fragments for containers, builds, tests, static checks, DT checks, and KUnit.

Important sections: global variables pin `DRM_CI_PROJECT_PATH`, `DRM_CI_COMMIT_SHA`, `UPSTREAM_REPO`, `TARGET_BRANCH`, `IGT_VERSION`, deqp runner, ci-templates commit, MinIO/S3 paths, LAVA tags, runner priority tags, artifact URLs, and environment-variable filtering. `default.before_script` downloads Mesa CI scripts/bin from the pinned commit, sets up test environment, and materializes an S3 JWT file; `after_script` restores JWT to the environment if present. Includes pull freedesktop ci-templates, many Mesa CI fragments, local DRM CI files, and lab-status YAML. Stages span sanity, container, deploy, git archive, build, static checks, kunit, validation, and per-driver hardware stages. Rule anchors distinguish merge attempt, post-merge, merge request, fork push, scheduled, and direct push pipelines. `make-git-archive` publishes a source archive to S3. `sanity` checks image tag length. Test job templates and concrete jobs define LAVA/crosvm execution for MSM, Rockchip, i915, amdgpu, MediaTek, Meson, Panfrost/Panthor, virtio_gpu, and vkms.

Control flow: local fragment includes define most jobs; this file supplies common variables, stages, and rule sets. Build/container jobs run automatically for merge/scheduled pipelines but are often manual for MRs/forks, depending on rules. Hardware tests consume artifacts uploaded by build jobs.

State and persistence: writes temporary Mesa CI scripts into the working directory, S3 JWT file `/s3_jwt`, downloaded Mesa CI fragments, Git archive tarball, and MinIO artifacts through downstream scripts.

Dependencies and integration points: highly coupled to Mesa CI templates, freedesktop ci-templates, lab-status, MinIO, LAVA farms, deqp-runner, IGT artifacts, kernel build artifacts, and GitLab environment variables. Local files `image-tags.yml`, `container.yml`, `static-checks.yml`, `build.yml`, `test.yml`, `check-devicetrees.yml`, and `kunit.yml` extend this scaffold.

Risks: many external includes are pinned but still represent a large imported CI surface. The default script downloads and overwrites `.gitlab-ci*` and `bin`, so local file names can collide. S3/JWT handling is sensitive; variables are intentionally unset after writing token files. Hardware job rule complexity can cause jobs to run ahead of artifact producers if dependencies are wrong. Device lists and runner tags can drift from lab availability.

Test signals: pipeline lint expansion, pinned Mesa CI download success, sanity tag-length check, source archive upload, job scheduling for MR/merge/scheduled/fork paths, S3 token availability, and LAVA jobs finding rootfs/kernel artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/gitlab-ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/igt_runner.sh -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/igt_runner.sh

Purpose: runs IGT on the device under test, applying driver-specific xfail lists, sharding the generated CI test list, producing JUnit output, and converting lockdep failures into a special allowed-failure exit code.

Important behavior: the script sources Mesa CI `setup-test-env.sh`, exports `IGT_FORCE_DRIVER=$DRIVER_NAME`, extends `PATH` and `LD_LIBRARY_PATH` for `/igt`, dumps DRM debug state, optionally moves installed modules into `/lib/modules` and modprobes `amdgpu`, `vkms`, or `panthor`, loads skip/flake/fail baseline files from `/install/xfails/$DRIVER_NAME-$GPU_VERSION-*`, maps `uname -m` to artifact arch, downloads `${PIPELINE_ARTIFACTS_BASE}/$ARCH/igt.tar.gz` and extracts it to `/`, shards `/igt/libexec/igt-gpu-tools/ci-testlist.txt` using `CI_NODE_INDEX/CI_NODE_TOTAL`, ensures `core_getversion` is present, runs `igt-runner`, converts failures CSV to JUnit with `deqp-runner junit`, then checks `/proc/lockdep_stats` and returns 101 if lockdep disabled itself while tests otherwise passed.

Control flow: `set +e` surrounds IGT so reporting can still run. The final exit code is IGT's return unless lockdep overrides success to 101. Sharding uses in-place `sed -ni`.

State and persistence: writes results under `$RESULTS_DIR`, mutates `/lib/modules`, downloads/extracts `/igt`, edits the test list in place, and writes JUnit XML.

Dependencies and integration points: depends on Mesa setup scripts, `curl`, IGT archive from `build-igt.sh`, deqp-runner, module install artifacts, xfail files, GitLab sharding variables, and driver variables from `test.yml`.

Risks: `cd $oldpath` references a variable not set in this file; it may rely on sourced environment. Download uses `tar --zstd` on a `.tar.gz` filename, which assumes GNU tar auto-detect or a mismatched option tolerance. Missing xfail files are tolerated. Sharding and appending `core_getversion` can mutate shared test list if multiple runners share extraction, though jobs normally have isolated rootfs.

Test signals: successful module load for module-backed drivers, artifact download per architecture, xfail application, sharded test list includes `core_getversion`, JUnit artifact creation, and lockdep exit 101 path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/igt_runner.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/image-tags.yml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/image-tags.yml

Purpose: centralizes the pinned container, kernel rootfs, firmware, and conditional build tags used by DRM CI templates.

Important variables: `CONTAINER_TAG` drives Debian and Alpine build/test image tags. `KERNEL_TAG` and `KERNEL_REPO` select the default kernel/rootfs baseline before the tested kernel is injected. `PKG_REPO_REV`, `FIRMWARE_TAG`, and `FIRMWARE_REPO` pin package and firmware sources. Conditional tags pin ANGLE, crosvm, and Piglit builds, with `CROSVM_TAG` aliased to the conditional crosvm tag.

Control flow: pure GitLab variable data, included by `gitlab-ci.yml` and consumed by freedesktop/Mesa templates and local jobs.

State and persistence: affects container image names and downloaded artifacts; no direct file writes.

Dependencies and integration points: coupled to the sanity job in `gitlab-ci.yml`, which enforces short image tag strings for selected variables, and to `lava-submit.sh` firmware overlay URLs.

Risks: stale tags break reproducibility or can point to unavailable S3 artifacts. Variable names must match upstream template expectations. Long tag values can fail the sanity check.

Test signals: pipeline variable expansion, sanity tag-length pass, container cache hits, rootfs/kernel artifact lookup under `gfx-ci/linux`, and firmware overlay downloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/image-tags.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/kunit.sh -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/kunit.sh

Purpose: runs DRM KUnit tests for the selected architecture using LLVM and the `drivers/gpu/drm/tests` KUnit configuration.

Important behavior: requires `KERNEL_ARCH` and `LLVM_VERSION`, runs `setup-llvm-links.sh`, prepends `/usr/bin` to `PATH`, then executes `./tools/testing/kunit/kunit.py run --arch "$KERNEL_ARCH" --make_options LLVM=1 --kunitconfig=drivers/gpu/drm/tests`.

Control flow: `set -euxo pipefail` aborts on missing variables or failed commands. Architecture-specific QEMU dependencies are installed by `kunit.yml`.

State and persistence: KUnit creates its normal build/test outputs under the kernel tree; no custom artifacts are written by this script.

Dependencies and integration points: depends on LLVM symlinks, kernel KUnit tooling, QEMU packages for target architecture, and the DRM tests KUnit config. Invoked by `kunit:*` GitLab jobs.

Risks: LLVM symlink setup writes to `/usr/bin`. KUnit architecture names must match KUnit's supported `--arch` values (`arm`, `arm64`, `x86_64`). Missing QEMU or incompatible kernel configs cause test boot failures rather than compile-only failures.

Test signals: KUnit compile and boot for all three architectures, `drivers/gpu/drm/tests` discovery, LLVM toolchain selection, and nonzero exit on failing KUnit assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/kunit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/kunit.yml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/kunit.yml

Purpose: defines GitLab CI jobs that run DRM KUnit tests on arm32, arm64, and x86_64 with LLVM and QEMU.

Important jobs/templates: `.kunit-packages` installs clang/lld/llvm for `$LLVM_VERSION`. `.kunit-base` runs in the `kunit` stage with 30 minute timeout, shallow clone depth, and script `drivers/gpu/drm/ci/kunit.sh`. `kunit:arm32`, `kunit:arm64`, and `kunit:x86_64` extend the corresponding build templates, add the shared LLVM packages, and install `qemu-system-arm`, `qemu-system-aarch64`, or `qemu-system-x86`.

Control flow: jobs inherit build rules and architecture variables from `.build:*`, so scheduling follows the top-level CI policy.

State and persistence: no explicit artifacts; KUnit output appears in job logs.

Dependencies and integration points: depends on `build.yml` templates, Debian package availability, `kunit.sh`, LLVM version from imported containers, and kernel KUnit infrastructure.

Risks: no artifacts are collected for postmortem beyond logs. QEMU package names can change with Debian base images. KUnit failures and infrastructure failures both fail the job unless logs are inspected.

Test signals: all three jobs expand with correct `KERNEL_ARCH`, packages install, `kunit.py run` boots each architecture, and failure logs clearly show failing KUnit cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/kunit.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/lava-submit.sh -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/lava-submit.sh

Purpose: prepares and submits a LAVA hardware test job for DRM CI, assembling the rootfs, kernel artifact overlay, optional firmware overlays, DUT environment variables, and structured job metadata.

Important behavior: sources `${FDO_CI_BASH_HELPERS}`, uses `fdo_find_s3_path "$LAVA_ROOTFS_PATH"` to locate a rootfs, creates `results/`, writes filtered environment variables to `dut-env-vars.sh`, appends `SCRIPTS_DIR=$CI_PROJECT_DIR/install`, tails `results/lava.log`, builds `LAVA_EXTRA_OVERLAYS` for optional firmware tarballs and mandatory `kernel-files.tar.zst`, then calls `lava-job-submitter` with farm, device type, boot method, timeout, rootfs, kernel URL prefix, DTB, env file, JWT file, kernel image details, visibility group, tags, Mesa job name, structured log path, SSH client image, project metadata, start section, and submit action.

Control flow: if rootfs lookup fails, the script emits a structured error and exits 1 before submission. The `tail -f` keeps LAVA log output streaming during submit.

State and persistence: writes `results/lava.log`, `results/lava_job_detail.json`, and `dut-env-vars.sh`; submits an external LAVA job; consumes S3 artifacts from build jobs.

Dependencies and integration points: depends on Mesa CI bash helpers, `lava-job-submitter`, MinIO/S3 paths, LAVA farm variables from `test.yml`, firmware variables from `image-tags.yml`, kernel artifacts uploaded by `build.sh`, and GitLab JWT file.

Risks: artifact lookup is time/order sensitive; the error text explicitly calls out missing dependencies. Word-splitting is intentionally allowed for several LAVA variables. Firmware overlay URLs are constructed from unvalidated names. A long-running `tail -f` is backgrounded and relies on job teardown to clean it.

Test signals: rootfs lookup success/failure, generated DUT env file excluding sensitive vars, overlay list with kernel and firmware, submitted LAVA YAML/log, structured job detail JSON, and correct timeout derived from `CI_JOB_TIMEOUT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/lava-submit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/setup-llvm-links.sh -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/setup-llvm-links.sh

Purpose: normalizes versioned LLVM tool names to unversioned names in `/usr/bin` for kernel build scripts that expect `clang`, `ld.lld`, `llvm-ar`, and related tools.

Important behavior: with `set -euo pipefail`, the script uses `which` and `ln -svf` to point `/usr/bin/clang++`, `clang`, `ld.lld`, `lld`, `llvm-ar`, `llvm-nm`, `llvm-objcopy`, `llvm-readelf`, and `llvm-strip` at their `${LLVM_VERSION}`-suffixed binaries.

Control flow: missing `LLVM_VERSION` or any missing tool aborts the script. Symlinks are overwritten forcefully.

State and persistence: mutates `/usr/bin` inside the CI container.

Dependencies and integration points: used by `dtbs-check.sh` and `kunit.sh` after GitLab jobs install `clang-${LLVM_VERSION}`, `lld-${LLVM_VERSION}`, and `llvm-${LLVM_VERSION}`.

Risks: requires permission to write `/usr/bin`. Force-updating global symlinks can affect later commands in the same job. `which` output is unquoted inside command substitution but tool paths are expected to be simple.

Test signals: symlink targets resolve to installed LLVM version; subsequent `make LLVM=1` and KUnit runs use the intended compiler/linker; missing package causes early failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/setup-llvm-links.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/static-checks.yml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/static-checks.yml

Purpose: defines the merge-request checkpatch static-analysis job for DRM CI.

Important job: `check-patch` runs in `static-checks`, extends `.build` and the x86_64 build container, executes `drivers/gpu/drm/ci/check-patch.py`, and sets `CHECKPATCH_TYPES` to a curated list of commit-message, signoff, ID, indentation, bit-macro, and DOS line ending checks. Rules run the job only for `merge_request_event`.

Control flow: all non-MR cases fall through to never because no catch-all rule is provided.

State and persistence: no artifacts are declared; output is in job logs.

Dependencies and integration points: depends on `check-patch.py`, GitLab MR variables, Linux `scripts/checkpatch.pl`, and build/container templates from other CI files.

Risks: extending `.build` may bring artifact/script defaults that are mostly overridden but still couple this job to build templates. The check list is intentionally narrow, so other checkpatch categories are not covered. No artifacts means failures require log inspection.

Test signals: job appears only in MR pipelines, computes commit range against target branch, runs checkpatch with the configured type list, and fails on bad commit metadata/style.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/static-checks.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/test.yml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/test.yml

Purpose: defines DRM CI test job templates and concrete hardware/software IGT jobs that consume built kernels and IGT artifacts.

Important jobs/templates: `.allow_failure_lockdep` allows exit code 101. `.lava-test` provides common LAVA behavior: build rules, 1h30m timeout, scheduled/collabora/on-success rules, S3 token setup, extracting `artifacts/install.tar`, moving install payload into artifacts, and executing the packaged `lava-submit.sh`. `.lava-igt:*` templates specialize for arm32, arm64, and x86_64 with `HWCI_TEST_SCRIPT=/install/igt_runner.sh`, Debian arch, farm, dependencies on testing kernels, rootfs containers, and IGT build jobs. `.software-driver` runs x86_64 crosvm tests using `install/crosvm-runner.sh install/igt_runner.sh`. Concrete jobs cover MSM boards, Rockchip display and Mali GPUs, i915 Chromebooks, amdgpu Stoney, MediaTek display/Panfrost/Powervr placeholders, Meson display/Panfrost, virtio_gpu, and vkms, with per-device variables for DTB, boot method, firmware, parallel shard count, runner tags, image type, driver name, and GPU version.

Control flow: templates layer through GitLab `extends`, so driver-specific jobs inherit LAVA or crosvm mechanics plus stage labels. Parallel jobs split IGT through `CI_NODE_INDEX` consumed by `igt_runner.sh`. Some devices/jobs are hidden templates or disabled via rules.

State and persistence: consumes kernel/IGT/rootfs artifacts and LAVA/crosvm images; produces results directories and junit through runner scripts and Mesa CI infrastructure.

Dependencies and integration points: depends on `build.sh`, `build-igt.sh`, `igt_runner.sh`, `lava-submit.sh`, Mesa CI LAVA/crosvm templates, lab runner tags, firmware overlays, xfail files, and S3 paths from `gitlab-ci.yml`.

Risks: hardware availability and runner tags are external moving parts. Parallel shard counts are manually tuned per device. Artifact dependencies must align with upload paths and architecture names. Lockdep failures are allowed, so master gating must inspect allowed-failure semantics. Device variable drift can submit invalid DTB or boot method combinations.

Test signals: pipeline expands expected per-driver jobs, LAVA submissions contain correct DUT variables and overlays, crosvm software jobs boot the kernel and run IGT, parallel shards divide test lists, xfail baselines are applied by driver/GPU version, and lockdep exit 101 is reported as allowed failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/Kconfig

Purpose: declares configuration options for in-kernel DRM clients, including fbdev emulation and the DRM boot logger, and selects the default client.

Important symbols: `DRM_CLIENT_LIB` builds the library and selects KMS helper/FB core when fbdev emulation is enabled. `DRM_CLIENT_SELECTION` is selected by drivers that support default clients and pulls in `DRM_CLIENT_LIB` for fbdev/log. `DRM_CLIENT_SETUP` enables client selection plumbing. Under "Supported DRM clients", `DRM_FBDEV_EMULATION` enables legacy fbdev/fbcon support, selects `DRM_CLIENT` and setup, and defaults to `FB`; `DRM_FBDEV_OVERALLOC` controls fbdev buffer over-allocation percentage; `DRM_FBDEV_LEAK_PHYS_SMEM` is an expert escape hatch for legacy userspace requiring physical addresses. `DRM_CLIENT_LOG` enables an on-screen kernel log client and selects draw/font support. A choice selects `DRM_CLIENT_DEFAULT_FBDEV` or `DRM_CLIENT_DEFAULT_LOG`, producing string `DRM_CLIENT_DEFAULT`.

Control flow: these options determine which C files are compiled and which client `drm_client_setup()` starts by default; the runtime module parameter can override the default.

State and persistence: Kconfig values persist in kernel `.config` and built modules. `DRM_FBDEV_OVERALLOC` affects runtime framebuffer allocation size.

Dependencies and integration points: ties DRM core, KMS helper, framebuffer console, `drm_client_setup.c`, `drm_fbdev_client.c`, and `drm_log.c` together. Drivers select `DRM_CLIENT_SELECTION` to opt into the client framework.

Risks: enabling fbdev leaks legacy interfaces into modern KMS drivers. `DRM_FBDEV_LEAK_PHYS_SMEM` is explicitly dangerous and unsupported. Default choice affects boot/user experience, especially whether fbcon or only boot logs appear.

Test signals: Kconfig dependency resolution for fbdev/log/default choices, compile with only fbdev, only log, both, or neither, and boot-time behavior of `drm_client_lib.active=`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/Makefile

Purpose: builds the DRM client library object and conditionally includes fbdev emulation and boot logger implementations.

Important entries: `subdir-ccflags-y += -I$(src)/..` lets client files include DRM internal headers from the parent directory. `drm_client_lib-y := drm_client_setup.o` is always included when `CONFIG_DRM_CLIENT_LIB` builds. `drm_client_lib-$(CONFIG_DRM_CLIENT_LOG) += drm_log.o` and `drm_client_lib-$(CONFIG_DRM_FBDEV_EMULATION) += drm_fbdev_client.o` add optional clients. `obj-$(CONFIG_DRM_CLIENT_LIB) += drm_client_lib.o` emits the final library object/module.

Control flow: Kconfig decides object composition; no runtime control exists here.

State and persistence: affects build artifacts only.

Dependencies and integration points: mirrors `clients/Kconfig` and the internal helper declarations in `drm_client_internal.h`.

Risks: object inclusion must stay synchronized with config guards in the internal header. Missing include path would break access to `drm_draw_internal.h`/DRM internals used by `drm_log.c`.

Test signals: builds for `DRM_CLIENT_LIB=m/y`, with and without `DRM_CLIENT_LOG` and `DRM_FBDEV_EMULATION`, and module symbol availability for exported setup functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_client_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_client_internal.h

Purpose: provides private declarations and stubs connecting `drm_client_setup.c` to optional fbdev and boot-log client implementations.

Important APIs/types: forward declares `struct drm_device` and `struct drm_format_info`. When `CONFIG_DRM_FBDEV_EMULATION` is enabled, declares `drm_fbdev_client_setup(struct drm_device *, const struct drm_format_info *)`; otherwise provides a no-op inline returning 0. When `CONFIG_DRM_CLIENT_LOG` is enabled, declares `drm_log_register(struct drm_device *)`; otherwise provides an empty inline.

Control flow: compile-time guards allow `drm_client_setup.c` to call optional clients without sprinkling callers with full implementation dependencies.

State and persistence: no state. It describes optional setup entry points.

Dependencies and integration points: consumed by DRM client library files and aligned with object selection in the clients Makefile.

Risks: stubs returning success can hide missing client support if callers assume setup had an effect. Declarations must match implementation signatures exactly because these functions are not public UAPI but are linked inside `drm_client_lib`.

Test signals: compile all config combinations and confirm `drm_client_setup()` behavior when defaults reference disabled clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_client_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_client_setup.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_client_setup.c

Purpose: exposes the public helpers drivers call after `drm_dev_register()` to start the selected in-kernel DRM client.

Important APIs/functions: module parameter `active` is stored in `drm_client_default` and defaults to `CONFIG_DRM_CLIENT_DEFAULT`. `drm_client_setup()` checks `DRIVER_MODESET`, then starts fbdev emulation when `active=fbdev`, starts the boot logger when `active=log`, warns on unknown non-empty values, and otherwise does nothing. `drm_client_setup_with_fourcc()` maps a 4CC to format info and delegates. `drm_client_setup_with_color_mode()` maps an old driver color mode to a 4CC via `drm_driver_color_mode_format()` and is documented as not preferred for new drivers. All three setup helpers are exported.

Control flow: selection is simple string comparison gated by compile-time config. fbdev setup return errors are warned and swallowed because the top-level setup helper is void.

State and persistence: `drm_client_default` is a read-only module parameter after init. Registered clients are owned by the DRM device and destroyed through `drm_dev_unregister()`.

Dependencies and integration points: depends on DRM core feature checks, format helpers, driver color mode mapping, `drm_fbdev_client_setup()`, and `drm_log_register()`. Drivers integrate by selecting `DRM_CLIENT_SELECTION` and calling one of these helpers after registering the device.

Risks: unknown runtime `active` values only warn and create no client, so fbcon/log output may disappear silently in automated boots. The setup helper is safe with no connectors and relies on client hotplug retry behavior. It warns if mode-setting is absent but otherwise cannot validate driver readiness.

Test signals: boot with `drm_client_lib.active=fbdev`, `log`, empty, and unknown; driver without `DRIVER_MODESET`; no-connector initial setup followed by hotplug; and wrapper functions with explicit formats/color modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_client_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_fbdev_client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_fbdev_client.c

Purpose: implements fbdev emulation as a `drm_client_dev`, letting DRM drivers expose legacy framebuffer/fbcon support through the generic DRM client lifecycle.

Important APIs/functions: `drm_fbdev_client_setup()` chooses a color mode from the preferred DRM format or device preferred depth, warns if the DRM device is not registered or already has `fb_helper`, allocates `drm_fb_helper`, prepares it, initializes a DRM client named `fbdev`, and registers the client. Client callbacks free/unprepare and `kfree()` the helper, unregister fully initialized framebuffer info or release partial clients, restore fbdev mode, handle hotplug, and suspend/resume fbdev. `drm_fbdev_client_hotplug()` initializes the helper lazily, disables unused functions for non-atomic drivers, runs initial config, and tears down on failure.

Control flow: setup only registers the client; actual framebuffer allocation may happen later on hotplug, so it is safe when no connectors exist yet. Restore and suspend/resume delegate to fb helper APIs.

State and persistence: `struct drm_fb_helper` holds fbdev state, framebuffer info, and embedded client. `dev->fb_helper` is set by fb helper initialization. The framebuffer persists until client unregister/device unregister.

Dependencies and integration points: depends on DRM client, fb helper, CRTC helper for legacy unused-output disable, format helpers, and device registration lifecycle. Started by `drm_client_setup()` when fbdev is selected.

Risks: setup returns allocation/init errors, but top-level `drm_client_setup()` only logs them. Color-mode derivation still maps through legacy bpp/depth assumptions. Non-atomic drivers get extra disable-unused behavior; atomic drivers rely on normal client modesets. Partial initialization path must release the DRM client without unregistering nonexistent fb info.

Test signals: fbcon on DRM drivers, no-connectors-at-setup then hotplug retry, non-atomic and atomic drivers, suspend/resume blanking, forced restore, preferred format/depth combinations, and failure injection in helper init/initial config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_fbdev_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_log.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_log.c

Purpose: implements an in-kernel DRM boot logger client that renders printk records onto DRM scanout buffers until userspace takes over.

Important APIs/types/functions: module parameter `scale` controls integer font scaling. `struct drm_log` contains a mutex, `drm_client_dev`, `console`, probed flag, scanout count, and scanout array. `struct drm_log_scanout` stores a client buffer, font, rows/columns, scaled glyph size, current line, format, pixel width, and colors. Rendering helpers convert glyph bitmaps through DRM draw blitters for 16/24/32-bit formats, clear rotating lines, wrap long printk records, and highlight timestamp prefixes. `drm_log_init_client()` probes modesets, allocates one dumb buffer per usable modeset, attaches them to mode sets, commits, and records scanouts. Client callbacks free scanouts, unregister the console, restore modesets, reset on hotplug, and suspend/resume the console. Console callbacks use nbcon `write_thread`, acquire the internal DRM master, and draw records under a mutex/migration lock. `drm_log_register()` allocates/registers the DRM client and console.

Control flow: scanout setup is lazy on first console write. Hotplug frees scanouts and clears `probed`, causing the next message to reprobe. Rendering is circular by line, clearing ahead to avoid stale text.

State and persistence: state is per DRM device: client registration, console registration, scanout buffers, current line position per scanout, and probed flag. Buffers are dumb client buffers and are deleted on hotplug/unregister.

Dependencies and integration points: depends on DRM client modeset helpers, dumb buffers, DRM draw internals, font support, printk console/nbcon, iosys maps, internal DRM master acquisition, and optional Kconfig `DRM_CLIENT_LOG`. Started by `drm_client_setup()` when selected.

Risks: drawing from console context is sensitive; the code uses nbcon locking and migration disable but still depends on vmap/flush safety. If no usable plane format can convert from XRGB8888, logging silently has no scanout. `drm_log_client_free()` frees `dlog` before logging through `client->dev`, relying on the saved `dev` pointer. The logger is for debugging and not a terminal, so users may confuse it with fbcon.

Test signals: boot logs visible before userspace, multiple connectors/modesets, hotplug reprobe, suspend/resume console behavior, different primary plane formats and font scales, timestamp coloring, and userspace DRM master takeover preventing further drawing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/Kconfig

Purpose: declares Kconfig options for DRM display helper infrastructure, including bridge connectors, DP AUX bus/chardev/CEC/helper support, DP tunnels, DSC, HDCP, HDMI audio/CEC/notifier/helper/state helpers.

Important symbols: `DRM_DISPLAY_DP_AUX_BUS` builds the OF-backed DP AUX endpoint bus. `DRM_DISPLAY_HELPER` is the umbrella tristate and selects CEC core when DP AUX CEC, HDMI CEC, or CEC notifier support is enabled. Inside the helper block, `DRM_BRIDGE_CONNECTOR` selects HDMI audio/CEC/state helpers for connector termination of bridge chains. `DRM_DISPLAY_DP_AUX_CEC` enables CEC tunneling over DP AUX. `DRM_DISPLAY_DP_AUX_CHARDEV` enables `/dev/drm_dp_auxN`. `DRM_DISPLAY_DP_HELPER`, `DRM_DISPLAY_DP_TUNNEL`, `DRM_DISPLAY_DSC_HELPER`, `DRM_DISPLAY_HDCP_HELPER`, `DRM_DISPLAY_HDMI_*` symbols control helper object compilation.

Control flow: symbols select object lists in `display/Makefile` and expose helper APIs to DRM drivers.

State and persistence: Kconfig state persists in `.config`; runtime state is in individual helper modules/files.

Dependencies and integration points: connects DRM core to DisplayPort, HDMI, bridge connector, CEC, HDCP, DSC, and tunnel helper code. `DRM_DISPLAY_DP_AUX_BUS` additionally requires OF.

Risks: helper options are interdependent; missing selects can lead to bridge connectors without needed HDMI/CEC/audio functionality. `DRM_DISPLAY_DP_TUNNEL_STATE_DEBUG` requires debug/ref-tracker dependencies and should stay expert-only.

Test signals: all helper combinations compile, selected symbols pull expected objects, bridge connector HDMI/audio/CEC features link, and DP AUX char device/bus options can be built as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/Makefile

Purpose: maps DRM display helper Kconfig symbols to compiled objects for the display helper module/library.

Important entries: `obj-$(CONFIG_DRM_DISPLAY_DP_AUX_BUS) += drm_dp_aux_bus.o` builds the AUX endpoint bus separately. `drm_display_helper-y := drm_display_helper_mod.o` is the base helper object. Conditional additions include bridge connector, DP dual-mode/helper/MST, DP tunnel, DSC, HDCP, HDMI audio/CEC/notifier/helper/state helpers, SCDC, DP AUX chardev, and DP AUX CEC. `obj-$(CONFIG_DRM_DISPLAY_HELPER) += drm_display_helper.o` emits the final helper object/module.

Control flow: Kconfig determines composition; module init in `drm_display_helper_mod.c` initializes the DP AUX char device when compiled in.

State and persistence: build artifact composition only.

Dependencies and integration points: mirrors display `Kconfig` and internal headers such as `drm_dp_helper_internal.h`.

Risks: helper APIs are widely exported; missing objects under a selected config causes link errors. Keeping DP AUX bus outside the umbrella helper means users must select the bus explicitly.

Test signals: compile each config combination, verify exported symbols link for DRM drivers, and module load/unload with DP AUX char device enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_bridge_connector.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_bridge_connector.c

Purpose: implements a generic DRM connector that terminates a chain of DRM bridges, delegating connector operations to the bridge closest to the connector that advertises each capability. It lets display controller drivers avoid writing connector glue for common bridge chains.

Important APIs/types/functions: `struct drm_bridge_connector` embeds `drm_connector`, stores the encoder and retained references to bridges providing EDID, HPD, detect, modes, HDMI, HDMI audio, DP audio, and HDMI CEC functionality, plus per-connector HDMI funcs. `drm_bridge_connector_init()` is the exported allocator/initializer. It walks the encoder bridge chain, collects the furthest EDID/modes/HPD/detect providers, validates that at most one HDMI/audio/CEC provider exists and that mandatory bridge callbacks are present, records connector type from the last bridge, inherits DDC, panel orientation, interlace/ycbcr constraints, supported HDMI formats, max bpc, and HDCP support, then initializes either an HDMI connector or generic connector and optional HDMI/DP audio and CEC helpers.

Control flow: detect delegates to the detect bridge when available, updates HDMI state and notifies all bridges; otherwise built-in panel-like connector types are assumed connected and other types unknown. HPD callbacks update connector status under mode-config mutex, notify every bridge's `hpd_notify`, and emit connector hotplug events. `get_modes()` prefers HDMI EDID already handled by HDMI detect, then EDID provider, then modes provider, else returns 0 for core fallback. HDMI infoframe and TMDS callbacks call through to the HDMI bridge. Audio callbacks dispatch to either HDMI or DP audio bridge. CEC callbacks dispatch to the selected HDMI CEC bridge.

State and persistence: bridge references are held until DRM managed cleanup via `drm_bridge_connector_put_bridges()`. Connector properties include polling mode, HDMI state, content protection property when HDCP is supported, panel orientation, and optional audio/CEC registration state.

Dependencies and integration points: depends on DRM bridge chain iteration, DRM connector helpers, atomic HDMI state helpers, EDID helpers, HDMI audio helper, HDMI CEC/notifier helpers, HDCP property helper, OF fwnode handling, and DRM managed allocation. Drivers use it after attaching bridge chains with `DRM_BRIDGE_ATTACH_NO_CONNECTOR`.

Risks: bridge ops flags are treated as contracts; advertising HDMI/audio/CEC without required callbacks returns `-EINVAL`. Multiple providers for exclusive roles return `-EBUSY`. EDID/modes selection is "last provider wins" and deliberately resets earlier providers. The detect path invokes HDMI hotplug state updates only when a detect bridge exists. Incorrect bridge type on the last bridge prevents connector creation.

Test signals: bridge chains with EDID, modes, detect, HPD, HDMI infoframes, audio, CEC notifier/adapter, panel orientation, HDCP, no-connector attach, hotplug notifications through every bridge, and invalid chains with duplicate providers or missing callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_bridge_connector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_display_helper_mod.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_display_helper_mod.c

Purpose: provides the module init/exit wrapper for the DRM display helper object.

Important APIs/functions: `drm_display_helper_module_init()` calls `drm_dp_aux_dev_init()`. `drm_display_helper_module_exit()` calls `drm_dp_aux_dev_exit()`. The module declares description and dual GPL/additional-rights license.

Control flow: helper module load initializes the DP AUX character device infrastructure when that feature is compiled in; unload unregisters it. Compile-time stubs in `drm_dp_helper_internal.h` make these calls no-ops when the char device is disabled.

State and persistence: state is owned by the DP AUX dev subsystem: character-device major, class, and IDR entries.

Dependencies and integration points: depends on `drm_dp_helper_internal.h` and the optional DP AUX char device implementation. It is the base object listed in the display Makefile.

Risks: module init failure prevents the whole display helper module from loading. Exit must run after all AUX devnodes are unregistered by their owners.

Test signals: module load/unload with `DRM_DISPLAY_DP_AUX_CHARDEV` enabled and disabled, char device class creation, and no stale `/dev/drm_dp_auxN` nodes after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_display_helper_mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_aux_bus.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_aux_bus.c

Purpose: implements the DisplayPort AUX endpoint bus, primarily for eDP panels described under an `aux-bus` child node of a DP AUX provider, so panel drivers can perform transactions over the AUX channel.

Important APIs/types/functions: `struct dp_aux_ep_device_with_data` extends `dp_aux_ep_device` with a `done_probing` callback. `dp_aux_bus_type` matches endpoint drivers by OF compatible, calls endpoint probe/remove/shutdown, and attaches/detaches PM domains. `of_dp_aux_populate_bus()` finds the `aux-bus` node, gets the first available child, marks it populated, allocates the endpoint device, assigns parent/bus/type/fwnode/name, and registers it. `of_dp_aux_depopulate_bus()` walks AUX device children and unregisters populated DP AUX endpoint devices. `devm_of_dp_aux_populate_bus()` wraps populate with a devm cleanup action. `__dp_aux_dp_driver_register()` and `dp_aux_dp_driver_unregister()` register endpoint drivers on this bus.

Control flow: endpoint probe attaches the PM domain powered on, calls driver probe, then calls `done_probing(aux)` if provided. If `done_probing()` returns `-EPROBE_DEFER`, the bus converts it to `-EINVAL` because deferring the already-probed panel would be wrong. Error paths invoke endpoint remove if needed and detach the PM domain.

State and persistence: OF child nodes are marked `OF_POPULATED` while the endpoint device exists, and node references are held by the device fwnode. Device memory is freed by the device release callback. PM domains remain attached for the endpoint lifetime.

Dependencies and integration points: depends on OF device matching, Linux device/bus model, PM domains, DRM DP AUX helper definitions, and panel/endpoint drivers using `dp_aux_ep_driver`. Used by bridge drivers such as SN65DSI86 to make AUX-connected panels probe beneath the AUX adapter.

Risks: only the first available child is populated, matching the assumption that one endpoint exists. Populated flag handling must stay balanced to avoid duplicate device creation or leaked OF refs. `done_probing()` contract is subtle and forbids deferral. Parent AUX must have been initialized (`aux->ddc.algo` warning).

Test signals: no-child `-ENODEV`, duplicate population `-EINVAL`, endpoint probe deferral behavior, done-probing success/failure, devm depopulation, PM domain attach/detach, and module/bus register/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_aux_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_aux_dev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_aux_dev.c

Purpose: exposes DisplayPort AUX adapters as character devices `/dev/drm_dp_auxN`, allowing userspace to read and write DPCD address space through normal file operations.

Important APIs/types/functions: `struct drm_dp_aux_dev` stores minor index, `drm_dp_aux *`, device node, kref, and active-use count. A global IDR and mutex allocate up to 256 minors; `AUX_MAX_OFFSET` limits file offsets to 1 MiB. `drm_dp_aux_register_devnode()` allocates an aux dev, creates a class device named `drm_dp_aux%d`, and keeps the initial reference. `drm_dp_aux_unregister_devnode()` clears `aux->drm_dev`, removes the IDR entry, drops `usecount`, waits for active I/O to drain, destroys the device, and drops the kref. File ops implement open/kref acquisition, fixed-size llseek, chunked read/write using `DP_AUX_MAX_PAYLOAD_BYTES`, signal interruption, iterator copy, and release/kref put. `drm_dp_aux_dev_init()` creates the class and registers a dynamic char major; exit unregisters both. Sysfs `name` reports the AUX adapter name.

Control flow: read/write increment `usecount` only if nonzero, preventing I/O after unregister starts. They truncate I/O at the AUX address-space limit and loop in payload-sized chunks, updating file position by bytes successfully transferred.

State and persistence: global class, char major, IDR entries, per-device krefs/usecounts, and device nodes persist while AUX adapters are registered. Open file descriptors hold krefs until release; unregister waits for active operations but existing file private data is invalidated for new I/O by usecount zeroing.

Dependencies and integration points: depends on Linux char device/class/IDR/kref/uio APIs and DRM DP DPCD read/write helpers. Called by DP AUX registration paths through internal helper declarations.

Risks: direct userspace DPCD access can perturb display hardware. Partial reads/writes return transferred byte counts, so tools must handle short I/O. Unregister must avoid stale DRM device references, hence `aux->drm_dev=NULL`. Long-running userspace I/O can delay unregister until usecount drains.

Test signals: devnode creation/removal, sysfs name, concurrent open/read/write during unregister, offset bounds, signal-interrupted I/O, payload chunking, and no use-after-free with open descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_aux_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_cec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_cec.c

Purpose: implements HDMI CEC tunneling over DisplayPort AUX for DP-to-HDMI/USB-C-to-HDMI adapters that advertise the DP CEC tunneling DPCD capability.

Important APIs/functions: CEC adapter ops write `DP_CEC_TUNNELING_CONTROL` to enable, update `DP_CEC_LOGICAL_ADDRESS_MASK`, write TX message buffer/info with retry count, optionally toggle snooping, and print adapter status from DP branch descriptor. `drm_dp_cec_irq()` handles IRQ_HPD service interrupts by checking `DP_DEVICE_SERVICE_IRQ_VECTOR_ESI1`, reading tunneling IRQ flags, receiving RX messages, reporting TX success/error/NACK to CEC core, and clearing flags. `drm_dp_cec_attach()` creates or updates a CEC adapter based on current DPCD capabilities and connector physical address, including monitor-all and multi-logical-address capability. `drm_dp_cec_set_edid()` derives physical address from EDID; `drm_dp_cec_unset_edid()` invalidates it and optionally schedules delayed unregister; register/unregister connector helpers initialize delayed work and tear down the adapter.

Control flow: all public paths first reject AUX adapters without a transfer function. `aux->cec.lock` protects adapter lifecycle and DPCD capability checks. The module parameter `drm_dp_cec_unregister_delay` debounces HPD low events, with 0 immediate unregister and values >=1000 meaning never unregister.

State and persistence: state lives in `aux->cec`: connector pointer, CEC adapter pointer, lock, and delayed unregister work. Hardware state is DPCD CEC control/logical-address/TX/RX registers. Adapter lifetime tracks EDID/HPD capability rather than merely connector lifetime.

Dependencies and integration points: depends on CEC core, DRM connector/EDID helpers, DP DPCD helpers, and IRQ_HPD handling by DP drivers. Used by drivers that call DP CEC register/attach/unset functions when connector EDID or HPD changes.

Risks: many adapters advertise tunneling but lack a physical CEC wire, producing isolated `/dev/cecX` devices. MST CEC is not supported. DPCD reads may fail when HPD is low; delayed unregister intentionally trades stale device presence for HPD glitch tolerance. `attempts - 1` underflows if CEC core ever passes zero attempts, though normal CEC callers should not.

Test signals: known working DP-to-HDMI adapters, CEC adapter creation/removal on EDID changes, HPD glitch debounce, RX/TX IRQ handling, logical address programming, monitor-all capability, and unregister-delay module parameter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_dual_mode_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_dual_mode_helper.c

Purpose: provides helper functions for detecting and controlling DisplayPort dual-mode (DP++) adaptors, including Type 1/Type 2 HDMI/DVI adaptors and LSPCON mode switching.

Important APIs/functions: `drm_dp_dual_mode_read()` and `drm_dp_dual_mode_write()` access adaptor registers at I2C slave address `0x40`; reads always start at offset zero and discard leading bytes when needed to handle adaptors without sub-addressing. `drm_dp_dual_mode_detect()` reads HDMI ID and adaptor ID to classify unknown/native, Type 1 DVI/HDMI, Type 2 DVI/HDMI, or LSPCON. `drm_dp_dual_mode_max_tmds_clock()` returns native unlimited, Type 1 fixed 165 MHz, or Type 2 register-derived limits. `drm_dp_dual_mode_get_tmds_output()`/`set_tmds_output()` read or control Type 2 TMDS output buffers, with write-read verification retries for LSPCON low-power behavior. `drm_dp_get_dual_mode_type_name()` maps enums to strings. `drm_lspcon_get_mode()` reads current level-shifter/protocol-converter mode with retries, and `drm_lspcon_set_mode()` writes requested mode and polls until the mode changes or times out.

Control flow: Type 1 adaptors often lack registers; failures reading the HDMI ID return `UNKNOWN`, leaving native HDMI versus Type 1 DVI decisions to driver-specific detection. Type 2 and LSPCON behavior depends on register reads. LSPCON set loops in 10 ms increments until timeout.

State and persistence: no driver state is stored here. State is adaptor hardware registers accessed through the DDC/I2C adapter.

Dependencies and integration points: depends on Linux I2C, DRM device logging, and public DP dual-mode register definitions. GPU drivers call these helpers during HDMI/DP++ detection, mode validation, and output enable/disable.

Risks: adaptor register behavior is inconsistent; helper deliberately uses conservative fallbacks. `drm_dp_dual_mode_read()` may allocate `size + offset` bytes and asks I2C to read that whole span, so callers should keep sizes bounded. Type misdetection can lead to wrong TMDS limits or buffer control. LSPCON mode changes depend on adaptor firmware timing.

Test signals: native HDMI ports, Type 1 DVI/HDMI adaptors with no registers, Type 2 adaptors, LSPCON adapters, max TMDS register edge values 0/0xff, TMDS output set verification retries, and LSPCON mode-change timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_dual_mode_helper.c -->
