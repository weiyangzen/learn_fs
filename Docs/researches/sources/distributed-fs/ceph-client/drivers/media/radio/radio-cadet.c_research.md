# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-cadet.c

Purpose: standalone ISA V4L2 driver for the ADS Cadet AM/FM/RDS card. Unlike most ISA FM drivers here, it supports AM and FM bands, RDS read capture, PnP/probing, and custom file operations.

Important types/APIs: global `struct cadet cadet_card` stores V4L2/video devices, control handler, I/O port, AM/FM band flag, current frequency, tune/signal state, wait queue, RDS polling timer, ring buffer indexes, mutex, and read state. Key functions include `cadet_gettune/getfreq/settune/setfreq`, RDS timer/read/poll helpers, V4L2 tuner/frequency/band ioctls, mute control, PnP probe, unsafe I/O probing, module init, and exit.

Control flow: init optionally registers PnP, falls back to probing a fixed list of ports by tuning/reading back FM frequency, claims a two-byte I/O region, registers V4L2 device/control/video node, defaults to FM low frequency, and tunes hardware. Frequency setting chooses AM versus FM by midpoint, encodes a 25-bit FIFO command, tries four tuning sensitivity values, updates signal strength from a table, and resets RDS. RDS starts lazily on read/poll, uses a 50 ms timer to drain the hardware FIFO into a 256-byte ring, wakes readers, and stops the timer when the last file is released.

State and persistence: all driver state is global single-device memory. RDS state persists while a file is open. Hardware frequency/mute persists until retuned or module exit mutes the device.

Dependencies and integration: ISA I/O, optional PnP IDs, V4L2 tuner/frequency-band/RDS capture APIs, timers, wait queues, and control events.

Risks: single global instance, unsafe port probing, ring-buffer index wrap relies on 8-bit fields and simple overflow handling, timer uses trylock and reschedules continuously while active, and read copies at most a stack `RDS_BUFFER`. Test signals include AM/FM band enumeration, RDS read/poll blocking and nonblocking behavior, PnP and manual I/O selection, tune readback, unload timer cleanup, and `v4l2-compliance` including RDS capability.
