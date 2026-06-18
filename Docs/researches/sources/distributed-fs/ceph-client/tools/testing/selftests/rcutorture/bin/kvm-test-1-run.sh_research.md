# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run.sh

Purpose: builds or reuses one rcutorture scenario kernel, generates qemu command and bare-metal reproduction instructions, and optionally runs qemu.

Important APIs and functions: sources `functions.sh` and per-suite `ver_functions.sh`; `config_override_param()` layers config fragments; calls `kvm-build.sh`, `identify_qemu`, `identify_boot_image`, `configNR_CPUS.sh`, `configfrag_boot_*`, `specify_qemu_cpus`, `specify_qemu_net`, `identify_qemu_args`, `identify_qemu_append`, `per_version_boot_params`, `kvm-test-1-run-qemu.sh`, `parse-build.sh`, and `parse-console.sh`.

Control flow: create combined ConfigFragment from common, scenario, and command-line options; if rerun base has kernel, reuse it, otherwise build; coordinate `build.wait`/`build.ready`; compute qemu args and boot args; write bare-metal recipe and qemu-cmd with embedded settings; if build-only, stop, else run qemu and parse console.

State and persistence: writes ConfigFragment files, build logs, kernel images, `.config`, `bare-metal`, `qemu-cmd`, run logs, and sentinel files.

Dependencies and integration: central worker invoked by generated `kvm.sh` scripts.

Risks and test signals: mutates kernel build tree and relies on many environment variables. Quoting in qemu-cmd assumes simple argument structure. Build-only and rerun paths rely on consistent result directory naming.
