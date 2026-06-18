# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/spca501.c

## Purpose
`spca501.c` is the GSPCA subdriver for SPCA501/SPCA501C raw video cameras. It supports several subtypes with distinct initialization tables, exposes raw `V4L2_PIX_FMT_SPCA501` modes at 160x120, 320x240, and 640x480, starts/stops the bridge isochronous packet engine, assembles raw frames, and maps five image controls to CCDSP/timing registers.

## Important APIs, types, and functions
`struct sd` stores cached control values, subtype, and the GSPCA base. Subtype constants cover Arowana, Intel Create and Share, Kodak DVC325, an Ori trace-derived unknown camera, Smile, ThreeCom HomeConnect Lite, and ViewQuest M318B. Static tables dominate the file: generic `spca501_init_data` and `spca501_open_data`, ThreeCom open data, Arowana init/open data, and Ori "mysterious" init/open data. Many table entries are annotated with Sunplus register functions such as timing generator, CCDSP, RGB-to-YUV matrix, gamma, window positions, and USB control.

`reg_write` sends one vendor control write. `write_vector` iterates a table until a `{0,0,0}` sentinel and stops on the first write error. `setbrightness`, `setcontrast`, `setcolors`, `setblue_balance`, and `setred_balance` write direct register values. The GSPCA callbacks are `sd_config`, `sd_init`, `sd_start`, `sd_stopN`, `sd_stop0`, `sd_pkt_scan`, and `sd_init_controls`.

## Control flow
Probe records subtype and enables all three raw modes. `sd_init` selects an initialization vector: Arowana/Smile use SPCA501C Arowana data, the Ori subtype uses its trace-derived open data at init time, and all other devices use generic SPCA501 defaults. `sd_start` then writes an open vector by subtype: ThreeCom special data, Arowana/Smile open data, Ori init data, or generic open data. After table setup, it writes the desired resolution to USB control register `0x07` using the current mode `.priv`, writes register `0x06`, and enables the packet engine by setting control register `2/index 1` to `0x02`.

`sd_stopN` disables the packet engine by clearing that control bit. `sd_stop0` writes GPIO/control index `0x05` to zero only if the device is still present. `sd_pkt_scan` interprets byte 0 as the packet marker: `0` starts a new frame, finalizes the prior frame, skips the 8-byte SPCA501 header, and adds the rest as `FIRST_PACKET`; `0xff` is dropped; all other packets skip one byte and become `INTER_PACKET`.

## State and persistence
The driver stores only subtype and current V4L2 control values in memory. All hardware configuration is volatile register state loaded from static tables on init/start. There is no persistent storage. Error propagation is partial: `write_vector` can fail, but `sd_start` does not check return values from every subtype vector or register write, so a failed write can be hidden until streaming produces bad frames.

## Dependencies and integration points
Dependencies are the USB control endpoint, GSPCA frame assembly, and V4L2 controls. The format is `V4L2_PIX_FMT_SPCA501`, so userspace needs the corresponding decoder or libv4l conversion path. `device_table` contains several real IDs and also an all-zero `USB_DEVICE(0x0000, 0x0000)` entry for the Ori trace-derived subtype, which is unusual and should be treated carefully by matching logic.

## Risks
The large trace-derived tables contain many magic values and conditional compile blocks, with comments indicating incomplete understanding. The all-zero USB ID is a matching hazard if not filtered by USB core behavior. Packet scanning lacks explicit length guards before skipping 8-byte headers or one-byte prefixes. Controls are only applied while streaming, so default cached values do not program hardware until user changes occur during a stream. `setcontrast` uses a 16-bit range split across timing registers `0x00/0x01`, which is unusual for a standard contrast control and may not match user expectations.

## Test signals
Test subtype-specific init/start vectors, all three resolutions, stream restart after stop0, raw frame boundaries from packet captures, short packet behavior, V4L2 brightness/contrast/saturation/red/blue balance writes, and USB ID matching around the zero-valued table entry. For regressions, compare output frame sizes against mode `sizeimage` and verify no frames are emitted after drop marker `0xff`.
