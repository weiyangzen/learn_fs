# sources/distributed-fs/ceph-client/drivers/input/mouse/focaltech.c

`focaltech.c` supports FocalTech PS/2 touchpads identified by PNP IDs `FLT0101`, `FLT0102`, and `FLT0103`. Detection is intentionally available even when full support is disabled so later psmouse probes do not confuse the hardware and fallback to basic PS/2 remains possible.

With full support, the driver tracks five fingers in `struct focaltech_hw_state`, decodes touch bitmap, absolute coordinate, and relative coordinate packets, reports MT slots and clickpad state, reads pad size through a proprietary register sequence, and switches to the FocalTech packet protocol. Initialization allocates `struct focaltech_data`, resets, reads size, switches protocol, configures a buttonpad input device, installs a 6-byte handler, disables resync, and replaces generic rate/resolution/scale setters with no-ops.

State is per-device finger active/valid flags, coordinates, width, pressed state, and max X/Y. Dependencies are psmouse, libps2, input-mt, and firmware PNP IDs. Risks include partial protocol knowledge, minimal packet validation, uncertain size calculation, invalid finger IDs, and hardware sensitivity to generic PS/2 tuning. Test signals include PNP-only detection, size/protocol-switch success, five MT slots, clamped and inverted coordinates, clickpad reporting, no resync, and reset/reconnect behavior.
