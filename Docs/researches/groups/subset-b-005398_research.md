# subset-b-005398 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/atomisp-ov2722.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/atomisp-ov2722.c

## Purpose
This file implements the V4L2 I2C subdevice driver for the OmniVision OV2722/OV2720 raw Bayer camera sensor used by AtomISP platforms. It owns sensor register access, probe/remove, platform power sequencing, CSI setup, mode selection, stream control, exposure programming, and a small volatile-control surface.

## Important APIs, Types, And Functions
- `ov2722_read_reg()`, `ov2722_write_reg()`, and `ov2722_i2c_write()` implement 16-bit register addressing over I2C with 8/16/32-bit reads and 8/16-bit writes. Register values are marshalled big-endian, matching sensor bus order.
- `ov2722_write_reg_array()` batches consecutive `struct ov2722_reg` entries into one transfer and flushes on gaps, delays, termination, or buffer pressure. It depends on `OV2722_TOK_TERM`, `OV2722_TOK_DELAY`, and `OV2722_MAX_WRITE_BUF_SIZE` from `ov2722.h`.
- `__ov2722_set_exposure()`, `ov2722_s_exposure()`, and `ov2722_ioctl()` expose AtomISP private exposure programming through `ATOMISP_IOC_S_EXPOSURE`. Coarse integration is shifted to sensor register format, VTS is extended when exposure plus margin exceeds the current frame length, analog gain is written to `OV2722_AGC_ADJ_H`, and digital gains are written to R/G/B manual white-balance gain registers.
- `ov2722_g_volatile_ctrl()` backs `V4L2_CID_EXPOSURE_ABSOLUTE` and read-only `V4L2_CID_LINK_FREQ`.
- `power_ctrl()`, `gpio_ctrl()`, `power_up()`, `power_down()`, and `ov2722_s_power()` implement the module sequencing contract through `struct camera_sensor_platform_data`.
- `ov2722_set_fmt()`, `ov2722_get_fmt()`, `ov2722_enum_mbus_code()`, `ov2722_enum_frame_size()`, and `ov2722_get_frame_interval()` provide the pad-format and frame-size V4L2 subdev operations.
- `ov2722_detect()` reads chip ID registers and accepts both `OV2722_ID` and `OV2720_ID`.
- `ov2722_probe()` allocates `struct ov2722_device`, obtains G-Min platform data, configures/detects the sensor, initializes controls/media entity state, and registers with AtomISP via `atomisp_register_i2c_module()`.

## Control Flow
Probe initializes a default preview resolution, registers the V4L2 subdev shell, obtains G-Min platform data for RAW10/GRBG, runs `ov2722_s_config()`, initializes controls, sets source-pad/media-entity metadata, and registers the I2C module with AtomISP. `ov2722_s_config()` power-cycles the sensor, enables CSI routing, detects the chip, and powers back down after probe-time validation.

Runtime power-on calls `power_up()` and then `ov2722_init()`, which resets the active global mode table to preview. `set_fmt()` chooses the nearest preview resolution, updates `dev->res`, `pixels_per_line`, and `lines_per_frame`, resets the sensor, and writes the selected register table. If startup fails, it retries the whole power-down/power-up/startup sequence up to `OV2722_POWER_UP_RETRY_NUM`. Streaming itself is a single write to `OV2722_SW_STREAM`.

Exposure control is serialized by `input_lock`; `ov2722_s_exposure()` validates analog gain is nonzero, then writes timing, exposure, analog gain, and digital gain registers. Querying exposure reads the three exposure bytes and assembles the sensor value for EXIF/control reporting.

## State And Persistence
Persistent driver state lives in `struct ov2722_device`: the active resolution pointer, cached line timing, platform callbacks, media pad, frame format, control handler, and link-frequency control. The file also mutates file-scope globals from `ov2722.h` (`ov2722_res` and `N_RES`) during init. Sensor programming is persisted in device registers until power-down/reset. There is no disk persistence.

## Dependencies And Integration Points
The driver depends on V4L2 subdev/media controller APIs, Linux I2C transfer APIs, ACPI matching for `INT33FB`, AtomISP private UAPI (`ATOMISP_IOC_S_EXPOSURE`, `struct atomisp_exposure`), G-Min platform helpers, and `camera_sensor_platform_data` callbacks for rails, GPIOs, clocks, and CSI configuration. It integrates with AtomISP by calling `atomisp_register_i2c_module()` after media entity setup and `atomisp_gmin_remove_subdev()` on remove/failure paths.

## Risks
- I2C read errors in `ov2722_detect()` are not checked before using ID bytes, which can turn bus failures into misleading ID failures.
- `ov2722_get_fmt()` reports `MEDIA_BUS_FMT_SBGGR10_1X10` while `ov2722_set_fmt()` assigns `MEDIA_BUS_FMT_SGRBG10_1X10`; the mismatch can confuse graph negotiation.
- `ov2722_remove()` assumes `dev->platform_data` is valid; incomplete probe paths use separate cleanup, but defensive checks would reduce crash risk.
- File-scope mutable resolution globals are shared driver state and would be fragile if multiple instances ever bind.
- The retry loop in `set_fmt()` performs power cycling under `input_lock`; slow or failing hardware can block other subdev operations.
- Exposure programming updates multiple registers without explicit group-hold transaction control in the function, so partial updates may be visible on hardware if the sensor is streaming.

## Test Signals
Useful validation includes successful ACPI/I2C probe for `INT33FB`, sensor ID detection for `0x2722` or `0x2720`, V4L2 media graph registration, enumeration of three preview frame sizes, format selection and startup for each mode, stream on/off register writes, `ATOMISP_IOC_S_EXPOSURE` with zero-gain rejection, link-frequency control values matching selected mode, and fault injection for I2C failures and power callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/atomisp-ov2722.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/gc2235.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/gc2235.h

## Purpose
This header defines the GalaxyCore GC2235 2M sensor interface used by its AtomISP I2C driver: register constants, tokenized register-write structures, device/resolution structures, stream-on/off tables, initialization tables, and supported preview resolution tables.

## Important APIs, Types, And Data
- Sensor identity and optical constants include `GC2235_ID`, focal length, f-number defaults, exposure timing margins, and register addresses for chip ID, reset, crop/output size, blanking, exposure, and gains.
- `struct gc2235_device` stores the V4L2 subdev, media pad, current mbus format, input mutex, control handler, selected `struct gc2235_resolution`, and AtomISP platform callbacks.
- `struct gc2235_resolution` describes each mode: dimensions, fps, pixel clock marker, line/frame timing, skip frames, and a pointer to its register table.
- `enum gc2235_tok_type` and `struct gc2235_reg` implement the register-list language consumed by the sensor driver. GC2235 registers are 8-bit addressed with 8/16/32-bit token values.
- `gc2235_stream_on[]` and `gc2235_stream_off[]` switch to page 3, start/stop MIPI via register `0x10`, and return to page 0.
- `gc2235_init_settings[]` contains sensor-wide reset, analog, black-level, gain, ISP, crop, and MIPI baseline configuration.
- Active preview modes are `gc2235_1600_900_30fps`, `gc2235_1616_1082_30fps`, and `gc2235_1616_1216_30fps`, exposed through `gc2235_res_preview`.

## Control Flow
The header itself has no executable control flow, but it defines the tables the companion driver writes during initialization, mode selection, and stream transitions. A typical sequence is: reset/init table, mode-specific crop/timing/MIPI table, `gc2235_stream_on[]`, then `gc2235_stream_off[]` before power-down or reconfiguration.

## State And Persistence
Mode state is represented by pointers into static register tables and by `gc2235_res`/`N_RES`, which default to the preview table. Runtime state is stored in `struct gc2235_device`; sensor state persists in hardware registers after table writes. The `used` field in resolution entries exists but defaults false in all table entries.

## Dependencies And Integration Points
The header includes V4L2 subdev, media entity, control, I2C, delay, and AtomISP platform headers. The driver consuming this file is expected to use `camera_sensor_platform_data`, media bus formats, and AtomISP private sensor-registration paths. Register tables depend on GC2235 register paging, especially page 3 for MIPI control and page 0 for main sensor control.

## Risks
- Non-preview modes are disabled behind `ENABLE_NON_PREVIEW` because the file says they are broken; callers must not assume still/video mode tables are present.
- Many register tables are magic hardware values with limited local derivation, so changes require hardware validation.
- The `pix_clk_freq` field is set to `30` in active modes, which looks like a placeholder rather than a real pixel clock and may mislead timing consumers.
- Register page switches are embedded in arrays; any interrupted write sequence can leave the sensor on the wrong register page.
- The mode description `"gc2235_1600_1066_30fps"` does not match the 1616x1082 dimensions, which can confuse logs/debugging.

## Test Signals
Validation should check chip ID `0x2235`, init table write completion, stream-on/off page transitions, mode enumeration for the three preview sizes, timing fields used by exposure code (`pixels_per_line`, `lines_per_frame`), correct MIPI packet width values, skip-frame behavior after mode set, and compile coverage with `ENABLE_NON_PREVIEW` both disabled and enabled if those dead tables are ever revived.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/gc2235.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/ov2722.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/ov2722.h

## Purpose
This header is the private data contract for the OV2722 AtomISP sensor driver. It defines sensor register addresses, tokenized register arrays, per-mode timing metadata, the `ov2722_device` runtime structure, and supported preview mode tables for the driver in `atomisp-ov2722.c`.

## Important APIs, Types, And Data
- Register constants cover software sleep/reset/streaming, chip ID, PLL, MIPI, exposure, gain, timing, crop, output size, and manual white-balance gain registers.
- `struct ov2722_device` holds V4L2/media state, the current resolution pointer, cached line/frame timing, platform callbacks, control handler, and the link-frequency control.
- `struct ov2722_resolution` describes a mode with dimensions, fps, pixel-clock marker, skip frames, line/frame timing, register table pointer, and `mipi_freq` in kHz.
- `enum ov2722_tok_type`, `struct ov2722_reg`, `struct ov2722_write_buffer`, and `struct ov2722_write_ctrl` support batched register table writes from the C driver.
- Active preview tables are `ov2722_1632_1092_30fps`, `ov2722_1452_1092_30fps`, and `ov2722_1080p_30fps`, exposed via `ov2722_res_preview`.
- Disabled tables include QVGA, 480P, VGA, 1M3, still, and video variants under `#if 0`, preserving older tuning data but excluding it from builds.

## Control Flow
The header is declarative, but the register table ordering encodes hardware control flow. Mode tables program crop/window timing, binning/subsampling, analog tuning, PLL/MIPI timing, manual 3A/gain defaults, power optimization registers, and exposure defaults before terminating with `OV2722_TOK_TERM`. The driver selects the nearest entry in `ov2722_res_preview`, writes its table during startup, and later uses the mode timing fields for exposure/VTS calculations and link-frequency reporting.

## State And Persistence
`ov2722_res` and `N_RES` are file-scope mutable globals initialized to preview mode data and reset by the C driver's init path. Static register arrays persist for the lifetime of the module. Runtime sensor state persists in OV2722 hardware registers until reset or power loss.

## Dependencies And Integration Points
The header depends on Linux I2C/V4L2/media-control headers and `atomisp_platform.h`. Its structures are consumed by the OV2722 I2C driver and indirectly by AtomISP through subdev registration, private exposure ioctls, media bus code negotiation, and link-frequency controls.

## Risks
- The header exposes mutable global mode pointers in a header file. Because only one C file includes it today this behaves as private storage, but including it elsewhere would create duplicate static state.
- Several mode tables and whole still/video arrays are compiled out, which preserves obsolete tuning but can hide bit rot.
- Mode output sizes are nonstandard near-1080 dimensions such as 1932x1092 and 1632x1092; downstream code must not assume exact 1920x1080.
- `mipi_freq` is absent for some disabled modes, so reviving them would break link-frequency control unless filled.
- Register arrays contain manual 3A and power optimization values; tuning changes can affect image quality, link stability, and power sequencing.

## Test Signals
Tests should verify the three preview modes enumerate in table order, nearest-size selection maps requested dimensions to expected entries, `pixels_per_line` and `lines_per_frame` match sensor register timing, link frequency reports 422400000 or 345600000 Hz as appropriate, all active register arrays terminate with `OV2722_TOK_TERM`, and the C driver can write each active array without exceeding the write-buffer logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/ov2722.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm.h

## Purpose
This header declares the high-level Host Memory Manager interface used by AtomISP/CSS code to allocate, map, copy, flush, and free ISP-addressable memory. It abstracts `hmm_bo` buffer-object management and exposes allocations as `ia_css_ptr` ISP virtual addresses.

## Important APIs, Types, And Functions
- `hmm_init()` and `hmm_cleanup()` initialize and tear down the global HMM buffer-object device.
- `hmm_alloc()` allocates private ISP-addressable memory, while `hmm_create_from_vmalloc_buf()` wraps an existing vmalloc buffer.
- `hmm_free()`, `hmm_load()`, `hmm_store()`, `hmm_set()`, and `hmm_flush()` provide allocation lifetime and CPU-side data movement/cache operations by ISP virtual address.
- `hmm_virt_to_phys()` resolves an ISP virtual address to a physical address for lower-level hardware programming.
- `hmm_vmap()`, `hmm_vunmap()`, and `hmm_flush_vmap()` expose BO pages as contiguous kernel virtual memory.
- `hmm_mmap()` maps an HMM allocation into a user VMA for video node mmap paths.
- `bo_device` is declared as the global `struct hmm_bo_device` backing this API.

## Control Flow
Typical use is initialize HMM at device startup, allocate an `ia_css_ptr`, transfer or map data with load/store/set/vmap/mmap, flush caches/TLB-relevant mappings where needed, and free the pointer at teardown. The comments require `hmm_vmap()`, `hmm_vunmap()`, and `hmm_mmap()` callers to pass the allocation start address returned by `hmm_alloc()`, not arbitrary interior addresses.

## State And Persistence
State is centralized in the global `bo_device`, whose internals are declared in `hmm_bo.h`. Allocations persist as ISP virtual address ranges plus backing pages until `hmm_free()`. There is no file persistence.

## Dependencies And Integration Points
The API depends on Linux memory management types, `hmm_common.h`, `hmm_bo.h`, and CSS `ia_css_types.h`. It integrates with AtomISP PCI/CSS memory paths, MMU mapping, vmap-based kernel access, cache maintenance, and V4L2 mmap handling.

## Risks
- The API exposes raw ISP virtual addresses; wrong or stale `ia_css_ptr` values can address the wrong BO unless implementations validate range ownership.
- Start-address-only requirements for vmap/vunmap/mmap are easy to violate from callers that hold interior offsets.
- Cache coherency depends on correct `hmm_flush()`/`hmm_flush_vmap()` use around CPU/ISP sharing.
- The global `bo_device` implies device-global state, so init/cleanup ordering and multi-device assumptions are important.

## Test Signals
Useful tests include alloc/free leak checks, load/store/set round trips, vmalloc-backed buffer import, vmap/vunmap reference behavior, mmap size validation, virt-to-phys mapping consistency, cache flush behavior under CPU/ISP sharing, and negative tests for null, freed, and interior ISP addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm_bo.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm_bo.h

## Purpose
This header declares the buffer-object layer underneath AtomISP HMM. It manages ISP virtual address allocation, page allocation/import, MMU binding, vmap/mmap exposure, refcounts, and searchable allocation metadata.

## Important APIs, Types, And Functions
- `struct hmm_bo_device` owns the ISP virtual address arena (`start`, `pgnr`, `size`), an `isp_mmu`, list/rbtree indexes for all/free/allocated BOs, locks, a status flag, and a slab cache.
- `struct hmm_buffer_object` represents one allocation with page array, mutex, type (`HMM_BO_PRIVATE` or `HMM_BO_VMALLOC`), mmap/vmap counts, status flags, vmap address, rb-tree node, address range, page count, and duplicate-size free-list links.
- Status flags include `HMM_BO_ALLOCED`, `HMM_BO_PAGE_ALLOCED`, `HMM_BO_BINDED`, `HMM_BO_MMAPED`, `HMM_BO_VMAPED`, `HMM_BO_VMAPED_CACHED`, and `HMM_BO_ACTIVE`.
- Device lifetime APIs are `hmm_bo_device_init()`, `hmm_bo_device_exit()`, and `hmm_bo_device_inited()`.
- BO lifetime and state APIs include `hmm_bo_alloc()`, `hmm_bo_release()`, `hmm_bo_ref()`, `hmm_bo_unref()`, `hmm_bo_allocated()`, `hmm_bo_alloc_pages()`, `hmm_bo_free_pages()`, `hmm_bo_bind()`, `hmm_bo_unbind()`, `hmm_bo_vmap()`, `hmm_bo_vunmap()`, `hmm_bo_mmap()`, and search helpers by ISP start, ISP range, and vmap start.

## Control Flow
The intended lifecycle is initialize the device with an MMU client and address arena, allocate a BO range, allocate or import physical pages, bind those pages into the ISP MMU, optionally vmap or mmap them for CPU/user access, then unmap/unbind/free pages and unref/release the BO. Device search APIs let higher layers translate `ia_css_ptr` or vmap addresses back to BO metadata for data movement and teardown.

## State And Persistence
State persists in the BO device's linked list, allocated/free rbtrees, MMU mappings, page arrays, and per-BO status bits. `rbtree_mutex` protects virtual address tree updates, `list_lock` protects the full BO list, and each BO has its own mutex for object state. The data is in-memory only.

## Dependencies And Integration Points
The layer depends on Linux list/rbtree/kref/mutex/spinlock/mm APIs, `isp_mmu.h` for hardware address translation, `hmm_common.h` diagnostics, and CSS `ia_css_types.h`. It is the main bridge between high-level HMM calls and the ISP MMU driver.

## Risks
- Correctness depends on strict status-bit transitions; missing rollback after partial page allocation, binding, vmap, or mmap can leak pages or leave stale MMU entries.
- The free-rbtree duplicate-size linked-list scheme has nontrivial invariants (`prev`/`next` only for same-page-count free nodes).
- Cache mode is tracked by status flags; mixing cached and uncached mappings needs careful enforcement.
- `VM_RESERVED` is mentioned in comments but is obsolete in newer kernels, so implementation compatibility should be checked.
- Search-by-range APIs must be used carefully to avoid accepting invalid interior addresses for operations that require allocation starts.

## Test Signals
Validation should cover arena initialization/exit, allocation/free fragmentation, rbtree coalescing or duplicate-size behavior, refcount release paths, page allocation and vmalloc import, MMU bind/unbind plus TLB flushing by callers, vmap cached/uncached transitions, mmap count handling, and search correctness for start, interior, boundary, and missing addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm_bo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm_common.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm_common.h

## Purpose
This small header centralizes HMM diagnostic guard macros used by the HMM and BO layers. The macros log to `atomisp_dev` and return or jump when common validation predicates fail.

## Important APIs, Types, And Macros
- `HMM_BO_NAME` names the subsystem as `"HMM"`.
- `var_equal_return()`, `var_equal_return_void()`, and `var_equal_goto()` check equality and log before returning or jumping.
- `var_not_equal_goto()` checks inequality and logs before jumping.
- `check_null_return()` and `check_null_return_void()` specialize the equality macros for null-pointer validation.

## Control Flow
These macros inject early-return and goto-based error paths into callers. They evaluate a condition, emit `dev_err(atomisp_dev, ...)`, and alter control flow with the supplied return expression or label.

## State And Persistence
The header owns no runtime state, but it depends on a visible `atomisp_dev` symbol in the includer/translation unit. Macro side effects include logging and early exit.

## Dependencies And Integration Points
The macros are consumed by `hmm_bo.h` wrappers and likely HMM implementation files. They assume kernel `dev_err()` is available and that `atomisp_dev` points to a valid device for logging.

## Risks
- Macro arguments may be evaluated in ways callers do not expect; avoid passing expressions with side effects.
- The hidden dependency on `atomisp_dev` makes the macros less reusable and can break compilation if included outside AtomISP contexts.
- Goto/return macros can obscure cleanup structure and make lock handling harder to audit.

## Test Signals
Compile coverage is the key signal. Runtime tests should exercise null and invalid-state paths under lockdep/KASAN to ensure early exits do not leak locks or resources and that logging is safe during init/teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp.h

## Purpose
This header is AtomISP's userspace-facing private V4L2 ABI. It defines ISP hardware revision constants, custom pixel/media-bus formats, statistics/configuration structures, parameter pointer bundles, private ioctls, private controls, private events, and custom color effects.

## Important APIs, Types, And Data
- Hardware constants describe ISP2300/ISP2400/ISP2401 revisions, steppings, and camera binary run modes.
- Custom formats include `V4L2_PIX_FMT_CUSTOM_M10MO_RAW` and several `V4L2_MBUS_FMT_CUSTOM_*` values.
- ISP tuning structs include noise reduction, temporal noise reduction, optical black, edge enhancement, 3A config/output/statistics, DVS/DIS coefficients and statistics, white balance, color correction, de-pixel noise, chroma enhancement, defect pixel correction, metadata, digital zoom, gamma, morphing, shading, MACC, CTC, overlay, exposure, and external ISP controls.
- `struct atomisp_parameters` is the large per-frame/global parameter bundle; most fields are pointers to specific tuning tables/configs and it ends with `per_frame_setting` by ABI requirement.
- Private ioctls under `BASE_VIDIOC_PRIVATE` configure or query ISP algorithms, 3A/DVS stats, tables, exposure, DZ, parameters, formats, fake events, array resolution, depth sync compensation, and sensor edge enhancement.
- Private controls include AtomISP postprocessing toggles, run mode, VFPP, continuous capture controls, raw buffer locking, exposure-zone count, digital zoom disable, and ISP version selection.
- Private V4L2 events signal 3A stats, metadata, acceleration completion, pause buffer, and CSS reset.

## Control Flow
The header does not execute code, but it defines ioctl/control/event contracts used by the AtomISP video-node implementation and by camera HAL userspace. Userspace populates ABI structs, sometimes with embedded `__user` pointers to large arrays, then submits private ioctls. Kernel code copies the outer structures, validates sizes/ranges, copies pointed-to buffers as needed, applies settings globally or per frame, and later emits stats/events with exposure/config IDs.

## State And Persistence
No state is stored in the header. ABI state is carried across ioctl calls in userspace-visible structs, queued per-frame parameter settings, and driver-side ISP/CSS configuration. Many structs intentionally expose persistent tuning tables that remain active until replaced.

## Dependencies And Integration Points
This file depends on Linux fixed-width types and V4L2 ioctl/control/event number spaces. It integrates every AtomISP layer that needs a stable ABI: video-node ioctl handling, sensor drivers using `struct atomisp_exposure`, CSS/ISP parameter translation, camera HALs, and media-controller pipelines.

## Risks
- ABI compatibility is the main risk: field reordering, type-width changes, or changing ioctl numbers breaks userspace.
- Several structs contain raw or `__user` pointers, including nested pointer bundles; ioctl handlers must validate and copy each pointed-to buffer carefully.
- Multiple ioctls intentionally share the same private number with different directions/types, especially DVS/DIS entries at offset 6. Dispatch code must disambiguate by command value exactly.
- Some comments contain stale or misspelled wording, but the bigger concern is that they may reflect old hardware assumptions.
- `struct atomisp_parameters` has a "keep at end" ABI warning for `per_frame_setting`; extensions must preserve layout expectations.
- Private V4L2 IDs can collide with upstream or vendor extensions if not isolated.

## Test Signals
Validation should include ioctl number ABI checks, 32/64-bit compat layout tests for every pointer-bearing struct, copy_from_user/copy_to_user fault injection, bounds checks for grids/tables/histograms, event delivery tests for stats/metadata/CSS reset, per-frame parameter ID round trips, and userspace smoke tests that exercise core private controls and `ATOMISP_IOC_S_EXPOSURE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp_gmin_platform.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp_gmin_platform.h

## Purpose
This header declares the G-Min platform integration helpers used by AtomISP sensor drivers on Intel MID/Atom camera platforms. It provides the bridge from a sensor V4L2 subdev to platform data, registration, variable lookup, and removal.

## Important APIs, Types, And Functions
- `atomisp_register_i2c_module()` registers a sensor subdev and its `camera_sensor_platform_data` with AtomISP.
- `atomisp_gmin_remove_subdev()` removes a G-Min-managed subdev.
- `gmin_get_var_int()` reads integer platform variables, likely from ACPI/device properties, with a default fallback.
- `gmin_camera_platform_data()` creates or returns `camera_sensor_platform_data` for a subdev using a declared CSI input format and Bayer order.

## Control Flow
Sensor probes call `gmin_camera_platform_data()` to obtain platform callbacks, use those callbacks during sensor configuration, then call `atomisp_register_i2c_module()` after V4L2/media initialization. Remove and failure paths call `atomisp_gmin_remove_subdev()`.

## State And Persistence
The header declares APIs only. Runtime state is held by the G-Min platform implementation and the returned `camera_sensor_platform_data`. No disk persistence is involved.

## Dependencies And Integration Points
It includes `atomisp_platform.h`, so it depends on V4L2 subdevs, AtomISP input formats, Bayer order enums, and camera platform data. It is the key integration point used by sensor drivers such as OV2722 to avoid board-specific hardcoding.

## Risks
- Sensor drivers assume returned platform callbacks are complete; missing callback validation can lead to null calls.
- Platform-variable defaults can mask ACPI/property misconfiguration.
- Removal must match registration exactly to avoid dangling subdev pointers in AtomISP platform tables.

## Test Signals
Tests should cover platform-data creation for supported sensors, default variable lookup, missing-property fallback, registration/removal idempotence on probe failure paths, and callback behavior for rails, GPIOs, FLIS clock, and CSI configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp_gmin_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp_platform.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp_platform.h

## Purpose
This header defines AtomISP platform-facing camera topology, CSI input formats, sensor platform callbacks, MIPI metadata, and SoC detection helpers. It is the common contract between AtomISP core, sensor drivers, and board/G-Min platform glue.

## Important APIs, Types, And Data
- `enum atomisp_bayer_order` describes raw Bayer ordering.
- `enum atomisp_input_stream_id` and `enum atomisp_input_format` describe CSI streams and MIPI data formats, including RAW, YUV, RGB, embedded, generic short packets, and user-defined data.
- `struct intel_v4l2_subdev_table` maps camera ports and lane counts to V4L2 subdevs.
- `struct atomisp_isys_config_info` and `struct atomisp_input_stream_info` describe per-stream input-system configuration and virtual-channel data.
- `struct camera_sensor_platform_data` provides callbacks for FLIS clock, CSI setup, GPIO lines, and voltage rails (`v1p8`, `v2p8`, `v1p2`).
- `struct camera_mipi_info` records port, lane count, input format, Bayer order, and metadata format/size/effective width.
- `atomisp_platform_get_subdevs()`, `atomisp_register_sensor_no_gmin()`, and `atomisp_unregister_subdev()` expose platform registration/enumeration.
- SoC macros identify Medfield, Bay Trail, Cherry Trail, Merrifield, Moorefield, and ISP2401-capable SoCs from `boot_cpu_data.x86_vfm`.

## Control Flow
Platform code registers or enumerates sensor subdevs with port/lane/format metadata. Sensor drivers receive `camera_sensor_platform_data`, use callbacks to power and route hardware, and pass `camera_mipi_info` to the host through V4L2 subdev host data. AtomISP core uses SoC macros and topology data to select hardware-specific configuration.

## State And Persistence
The header owns no state. Runtime state is held in platform tables, subdev host data, and callback implementations. The callback interface controls hardware state for clocks, regulators, GPIOs, and CSI routing.

## Dependencies And Integration Points
It depends on x86 CPU identification, Linux I2C, V4L2 subdevs, and `atomisp.h`. It integrates with sensor probe/configuration, AtomISP PCI core, G-Min helpers, and non-G-Min platform registration paths.

## Risks
- Callback pointers are optional by type but often assumed present by drivers; inconsistent validation can crash during power sequencing.
- `ATOMISP_INPUT_STREAM_GENERAL` and `ATOMISP_INPUT_STREAM_CAPTURE` both equal zero, which is intentional aliasing but can confuse generic code.
- SoC macros rely on `boot_cpu_data.x86_vfm`; portability outside intended Intel Atom platforms is limited.
- `metadata_effective_width` is a pointer, so ownership/lifetime must be clear when attached as host data.

## Test Signals
Validation should cover sensor registration/enumeration for G-Min and no-G-Min paths, correct port/lane/format propagation to CSI configuration, callback failure rollback in sensor drivers, SoC macro behavior on supported CPU IDs, and multi-stream virtual-channel configuration with embedded metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/mmu/isp_mmu.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/mmu/isp_mmu.h

## Purpose
This header declares AtomISP's classic two-level ISP MMU abstraction. It defines ISP page-table geometry, address translation macros, the hardware-client callback contract, MMU state, and map/unmap/TLB-flush APIs used by HMM buffer binding.

## Important APIs, Types, And Functions
- Page-table constants define 4 KiB pages, 10-bit L1 and L2 indexes, 1024 entries per level, and 2-level address decomposition.
- Macros convert ISP virtual addresses to L1/L2 indexes, align sizes, convert page counts to sizes, and test PTE validity.
- `struct isp_mmu_client` supplies hardware-specific behavior: driver name, PTE valid mask, null PTE, page-directory base conversion, TLB flush callbacks, and physical/PTE conversion helpers.
- `struct isp_mmu` stores the selected client, L1 page-table address/PTE, L2 page-table refcounts, physical base address, and `pt_mutex`.
- `isp_mmu_init()` and `isp_mmu_exit()` manage page table lifetime.
- `isp_mmu_map()` and `isp_mmu_unmap()` update mappings for contiguous physical pages at an ISP virtual address.
- `isp_mmu_flush_tlb_all()` and `isp_mmu_flush_tlb_range()` dispatch to client callbacks.

## Control Flow
HMM initializes an `isp_mmu` with a hardware client, maps each allocated BO page range into ISP virtual space, asks the hardware client to flush TLBs after mapping changes, and unmaps ranges during free/unbind. Map/unmap are internally mutex protected, but comments explicitly state they do not flush TLBs; callers must do that separately.

## State And Persistence
MMU state includes allocated L1/L2 page tables, L2 reference counts, the MMU client's callback table, and the hardware-facing page-directory base. Mappings persist in memory and hardware-visible page tables until unmapped or MMU exit.

## Dependencies And Integration Points
This header depends on kernel types/mutex/slab support and is consumed by `hmm_bo.h` and platform-specific MMU clients such as `sh_mmu_mrfld`. It bridges HMM buffer allocation to ISP hardware address translation.

## Risks
- TLB flushing is caller responsibility after map/unmap, making stale translations a likely integration bug.
- `ISP_PT_TO_VIRT` is defined with `do { ... } while (0)` and does not return a value, so it is unusable as an expression despite its name.
- Page size is required to match the kernel page size; unusual configurations would need careful review.
- `unsigned int` ISP virtual addresses limit address width and require range validation at callers.
- Client callbacks are partly mandatory by comment; init must enforce required callbacks to avoid null dereferences.

## Test Signals
Tests should cover address-index macros, size/page-count conversions, mapping and unmapping one page and multi-page ranges, L2 refcount behavior, TLB flush callback invocation by callers, null-PTE handling, physical/PTE conversion round trips for each hardware client, and invalid range/overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/mmu/isp_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/mmu/sh_mmu_mrfld.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/mmu/sh_mmu_mrfld.h

## Purpose
This header exposes the Merrifield-specific Silicon Hive/ISP MMU client descriptor for AtomISP. It lets generic ISP MMU/HMM code bind to Merrifield hardware-specific PTE and TLB behavior.

## Important APIs, Types, And Data
- `extern struct isp_mmu_client sh_mmu_mrfld;` declares the hardware client consumed by `isp_mmu_init()`.

## Control Flow
There is no executable logic in this header. Platform or AtomISP initialization code selects `sh_mmu_mrfld` and passes it to the generic MMU layer, which then calls its callbacks for page-directory base setup, PTE conversion, and TLB flushing.

## State And Persistence
The declaration points to implementation-defined static/global state elsewhere. Runtime MMU state is held in `struct isp_mmu`, not in this header.

## Dependencies And Integration Points
The header depends conceptually on `struct isp_mmu_client` from `isp_mmu.h`, though it does not include that file itself. It integrates Merrifield-specific MMU code with the generic AtomISP HMM/ISP MMU layer.

## Risks
- Because the header does not include `isp_mmu.h`, includers must have seen `struct isp_mmu_client` first or compilation fails.
- The external symbol must be provided exactly once by the Merrifield MMU implementation.
- Wrong client selection would corrupt page-table interpretation or TLB maintenance.

## Test Signals
Build tests should verify include ordering and symbol resolution. Runtime validation should initialize the generic MMU with `sh_mmu_mrfld`, map/unmap HMM buffers, verify PTE physical translations, and confirm Merrifield TLB flush callbacks run on mapping changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/mmu/sh_mmu_mrfld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp-regs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp-regs.h

## Purpose
This header collects AtomISP PCI/MMIO register offsets, bit masks, frequency constants, CSI receiver configuration values, power-management fields, and ISP2401 CSI2+ delay-register addresses used by the AtomISP PCI core.

## Important APIs, Types, And Data
- Common PCI/MSI interrupt registers include command/status, MSI capability/address/data, interrupt control, and `PCI_I_CONTROL`.
- Merrifield-specific CSI, power, deadline, trim, RCOMP, and PM registers are defined with offsets and bit fields such as `MRFLD_PCI_CSI_CONTROL_PARPATHEN` and `MRFLD_PCI_CSI_CONTROL_CSI_READY`.
- Read/write combining flags and reset masks configure internal bus behavior through `MRFLD_PCI_I_CONTROL_*`.
- CSI lane trim and receiver-selection constants configure SH versus Arasan CSI backend selection and per-port lane settings.
- Interrupt MMIO registers include clear, status, and enable offsets.
- ISP power/frequency constants define ISPSSPM fields, requested/guaranteed frequency masks, supported ISP frequencies, HPLL frequencies, and fuse register masks.
- CSI2+ delay constants enumerate port A/B/C bases, lane offsets, TERMEN/SETTLE offsets, and absolute addresses for clock/data lane delay registers.
- `DMA_BURST_SIZE_REG` and `ISP_DFS_TRY_TIMES` provide additional PCI-core tuning constants.

## Control Flow
The header is declarative; control flow lives in PCI core code that reads/writes these offsets during probe, power transitions, CSI receiver setup, interrupt handling, dynamic frequency scaling, lane timing adjustment, and DMA tuning. Bit masks are combined with register reads/writes to enable CSI paths, select receiver backends, configure lane counts, and manage ISP power/frequency.

## State And Persistence
State is held in PCI config space and AtomISP MMIO registers programmed with these constants. Register values persist until hardware reset, power transition, or later driver writes. The header itself owns no state.

## Dependencies And Integration Points
It depends on `BIT()` being available from includers and is consumed by AtomISP PCI/platform code. It integrates hardware register programming with sensor CSI topology from `atomisp_platform.h`, MMU/HMM memory behavior, interrupt handling, and power/frequency management.

## Risks
- Register offsets and masks are hardware-specific; using the wrong constants for a SoC revision can break CSI, interrupts, or power management.
- Absolute CSI2+ delay addresses assume a particular MMIO layout and should be gated by hardware generation.
- Some constants represent PCI config-space offsets while others are MMIO offsets; call sites must use the correct accessors.
- Frequency constants are integer MHz-like encodings; mismatched HPLL/fuse interpretation can select unsupported clocks.

## Test Signals
Validation should include PCI probe register-access smoke tests, interrupt enable/status/clear behavior, CSI receiver selection for each supported port/lane configuration, Merrifield/Cherry Trail generation gating, ISP power on/off state transitions, dynamic frequency requests with timeout handling using `ISP_DFS_TRY_TIMES`, and readback verification for CSI2+ settle/termen tuning registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp-regs.h -->
