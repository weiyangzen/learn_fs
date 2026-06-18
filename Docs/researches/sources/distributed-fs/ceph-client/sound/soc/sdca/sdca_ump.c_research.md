# sources/distributed-fs/ceph-client/sound/soc/sdca/sdca_ump.c

## Purpose
Shared UMP buffer ownership and message transfer helpers for SDCA features such as file download and HID reports.

## APIs, Types, and Functions
Exports `sdca_ump_get_owner_host()`, `sdca_ump_set_owner_device()`, `sdca_ump_read_message()`, `sdca_ump_write_message()`, `sdca_ump_cancel_timeout()`, and `sdca_ump_schedule_timeout()`.

## Control Flow, State, and Persistence
Ownership helpers read/write the owner control for a given entity/control. Read-message reads the SDCA message offset and length controls, validates them against the buffer start/length from the offset control range, allocates a buffer, and raw-reads from the device regmap. Write-message validates requested offset/length and direct UMP mode, raw-writes the payload into the device regmap buffer, then writes offset and length controls in the function regmap. Timeout helpers wrap delayed-work cancellation/scheduling on the default workqueue.

## Dependencies and Integration
Depends on regmap, SoundWire SDCA control address macros, parsed control ranges, and SDCA function/entity/control metadata. FDL and HID code use these helpers to transfer SWF data and HID reports.

## Risks and Test Signals
Risks include leaked allocated message buffers on raw-read failure, only direct UMP mode supported for writes, no ownership handoff inside read/write helpers themselves, and buffer arithmetic relying on valid parsed range data. Test signals are owner mismatch rejection, buffer overrun rejection, direct UMP firmware write, HID report read, delayed timeout cancellation/scheduling, and error-path memory checking.
