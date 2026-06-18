# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/storage_common.h

## Purpose
This header defines shared USB mass-storage gadget data structures, constants, descriptors, logging helpers, SCSI sense constants, and exported helper prototypes. It is the common contract for mass-storage function implementations that share LUN and descriptor handling.

## Important APIs, types, and functions
`struct fsg_lun` stores backing file state, sector geometry, flags, sense data, device object, names, and inquiry string. `struct fsg_buffhd` models a pipeline buffer with IN/OUT USB requests and buffer state. `enum fsg_buffer_state`, `enum fsg_state`, and `enum data_direction` describe transport and command-processing state used by mass-storage engines. Macros define `FSG_BUFLEN`, `FSG_MAX_LUNS`, command size, sense-code helpers, and inquiry string length. Extern declarations expose the shared descriptors and all LUN show/store/open/close helpers.

## Control flow
The header has no executable flow, but it shapes mass-storage command loops. Implementations use `fsg_buffhd` rings to receive CBWs, transfer data, and send CSWs; use `fsg_state` to handle resets, aborts, config changes, and exits; and call the LUN helpers to manage backing media under their own locks.

## State and persistence
State is in `struct fsg_lun` and buffer heads owned by including modules. The header documents fields that persist for the lifetime of a configured LUN, including open file references, media geometry, sense/unit attention data, and user-visible strings. Debug macros conditionally emit per-LUN messages.

## Dependencies and integration points
The header includes Linux device, USB storage, SCSI, and unaligned-access definitions. It integrates with the composite framework through descriptor externs and with SCSI command processing through sense constants and CDB sizes. `fsg_lun_from_dev()` maps device objects back to LUNs for sysfs callbacks.

## Risks and edge cases
Callers must respect locking around `fsg_lun` media fields and not dereference `filp` without checking `fsg_lun_is_open()`. Sense constants are packed integers interpreted by helper macros, so additions must preserve the SK/ASC/ASCQ encoding. Buffer state values include negative in-flight states, which can be mishandled if treated as booleans.

## Test signals
Compile all mass-storage functions, exercise LUN sysfs/configfs callbacks, run SCSI command tests for sense reporting, stress buffer state transitions under reset/disconnect, and validate FS/HS/SS descriptor consumers.
