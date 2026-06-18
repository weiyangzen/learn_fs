# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_ctrl.h

## Purpose
This header declares the MFC firmware, hardware lifecycle, PM, reset, and instance lifecycle APIs implemented by `s5p_mfc_ctrl.c`.

## Important APIs, Types, and Functions
The declarations cover firmware allocation/release/load, hardware init/deinit, sleep/wakeup, reset, open MFC instance, and close MFC instance. All functions operate on `struct s5p_mfc_dev` and, for instance lifecycle, `struct s5p_mfc_ctx`.

## Control Flow and State
There is no local flow. The functions declared here drive transitions at the device level and context level: firmware memory available, firmware loaded, hardware initialized, hardware sleeping/awake, firmware instance opened, and firmware instance closed.

## Dependencies and Integration Points
It includes `s5p_mfc_common.h` for device/context types and is used by core, PM, watchdog, probe/open/release, and possibly operation paths.

## Risks
The API has no explicit locking annotations, but callers must hold or coordinate with `mfc_mutex`, `hw_lock`, clocks, and wait queues depending on context. Misuse can race firmware init with open/release or suspend.

## Test Signals
Compile checks validate prototypes. Runtime coverage should call each API through normal open/close, first-open init, last-close deinit, suspend/resume, and watchdog recovery.
