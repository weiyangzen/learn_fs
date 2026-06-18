<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debug.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debug.h

Purpose: central trace-mask definitions for pvrusb2.

Important APIs/types/functions: `pvrusb2_debug` is the module-level trace mask. `pvr2_trace(msk, fmt, ...)` emits `pr_info()` when a mask bit is enabled. Mask definitions cover info/errors/tolerance/trap/std/init/start-stop/control/state/eeprom/context/sysfs/firmware/chips/I2C/encoder/buffer/data/debug/GPIO/DVB feed.

Control flow: all pvrusb2 files include this header and guard debug output by mask bits. Users enable bits through the module parameter defined elsewhere.

State and persistence: only the external integer trace mask. No persistent storage.

Dependencies and integration: integrates all pvrusb2 source files around a shared tracing vocabulary.

Risks: `pr_info()` can be noisy for high-volume data paths. The closing include-guard comment names a different header, which is harmless but confusing.

Test signals: set `pvrusb2_debug` to individual bits and confirm expected logs without flooding critical paths excessively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debug.h -->
