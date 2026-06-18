# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/fw.h

## Purpose
`fw.h` defines RTL8723AE firmware image bounds, firmware-header detection, H2C command byte setters, and public firmware command APIs.

## APIs, Types, And Constants
It defines firmware size/start/end/page constants, polling delay, `IS_FW_HEADER_EXIST`, and `pagenum_128`. H2C setters encode power mode, smart PS, beacon pass time, join-BSS status, and reserved-page locations. Public declarations cover generic H2C fill, firmware power mode, reserved pages, join-BSS report, and P2P PS offload.

## Control Flow, State, And Persistence
The header has no control flow. Its macros directly write command bytes into caller-provided buffers, so they shape firmware-visible state. The declared functions in `fw.c` persist settings in firmware mailboxes, reserved packet pages, and P2P hardware registers.

## Dependencies And Integration Points
It integrates `fw.c`, DM/power-save paths, join status notifications, P2P handling, and BT coexistence H2C command submission. It depends on firmware IDs and shared RTL8723 common firmware definitions included by implementation files.

## Risks And Test Signals
Risks are command layout drift, wrong firmware size assumptions, and unsafe macro use with undersized buffers. Signals include clean builds, successful firmware readiness, power-save entry/exit, join report handling, reserved-page H2C acknowledgements, and P2P PS behavior.
