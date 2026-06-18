# sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev.h

Purpose: Shared private header defining onboard USB device platform data and the OF match table used by both the platform driver and platform-device creation helper.

Important APIs and types: `MAX_SUPPLIES`, `struct onboard_dev_pdata`, per-device static pdata constants, and `onboard_dev_match[]`. Pdata includes reset pulse duration, power-on delay, regulator supply names, supply count, and whether the target is a hub.

Control flow: not executable by itself; match entries map USB-style DT compatibles such as `usb424,5744`, `usbbda,179`, `usb1da0,5511`, and `usb5986,1198` to pdata consumed by `onboard_usb_dev.c`. `onboard_usb_dev_pdevs.c` also calls `of_match_node()` on this table to decide whether to instantiate a platform device.

State and persistence: all data is compile-time static and read-only. Risks include table drift between this match table and the USB ID table in `onboard_usb_dev.c`, `MAX_SUPPLIES` limiting future devices to two supplies, and missing `is_hub` on `usb_a_conn_data` causing non-hub suspend policy. Test signals include each compatible selecting intended supplies/delays, build coverage for all table users, and DT binding tests for peer hubs and supply names.
