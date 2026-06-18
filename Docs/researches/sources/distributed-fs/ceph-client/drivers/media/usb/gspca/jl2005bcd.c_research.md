<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jl2005bcd.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jl2005bcd.c

Purpose: `jl2005bcd.c` supports JL2005B/C/D USB cameras using command bulk endpoint `0x03`, response endpoint `0x84`, and data endpoint `0x82`. It advertises a custom `V4L2_PIX_FMT_JL2005BCD` format for CIF or VGA camera families detected from firmware ID.

Important APIs, types, and functions: `struct sd` stores firmware ID, workqueue, frame brightness, block size, and selected mode family. Command helpers include `jl2005c_write2()`, `jl2005c_read1()`, `jl2005c_read_reg()`, and `jl2005c_write_reg()`. `jl2005c_get_firmware_id()` reads six identifying registers. Four stream-start helpers program large/small VGA/CIF modes. `jl2005c_dostream()` is the synchronous bulk capture worker.

Control flow: `sd_config()` enables bulk mode with a small core buffer, reads firmware ID, chooses CIF modes with 0x80-byte blocks when the first ID nibble is `0x4`, otherwise VGA modes with 0x200-byte blocks, and initializes work. `sd_start()` selects a register script by requested width and schedules the worker. The worker requests a new frame, validates the `JL` header, computes remaining bytes from header byte 7 times block size, then reads chunks until `LAST_PACKET`.

State and persistence: firmware ID and block size persist for the device lifetime. Frame-local state (`bytes_left`, `header_read`) lives in the worker. No V4L2 controls are provided.

Dependencies and integration points: depends on process-context USB bulk I/O, GSPCA stop0 flushing, and a custom userspace pixel format decoder.

Risks: capture stops on short reads or bad first block signature, with no recovery loop inside the worker. `sd_start()` returns success after scheduling even if later worker setup fails. Test signals include correct CIF/VGA detection, valid frame sizes, repeated stream restart without stuck work, and graceful handling of unplug during worker reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jl2005bcd.c -->
