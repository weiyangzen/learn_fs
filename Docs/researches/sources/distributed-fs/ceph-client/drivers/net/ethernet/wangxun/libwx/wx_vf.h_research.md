# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf.h

## Purpose
`wx_vf.h` defines the VF register map, descriptor-control bitfields, RSS/interrupt/queue constants, link-speed extraction helpers, and exported VF mailbox/hardware API declarations shared by Wangxun VF drivers.

## Important APIs, Types, and Functions
The header defines control registers (`WX_VXSTATUS`, `WX_VXCTRL`, `WX_VXMRQC`), VF interrupt registers (`WX_VXICR`, `WX_VXIMS`, `WX_VXIMC`, `WX_VXITR`, `WX_VXIVAR`), RX/TX descriptor registers, buffer-size encoding macros (`wx_buf_len`, `wx_hdr_sz`, `wx_buf_sz`), link extraction macros (`WX_PFLINK_STATUS`, `WX_PFLINK_SPEED`, `WX_VXSTATUS_SPEED`), and `struct wx_link_reg_fields`. It declares low-level VF functions implemented in `wx_vf.c`.

## Control Flow
The header has no executable control flow. VF reset, open, queue setup, mailbox commands, and link checks use these offsets and masks to program device state and interpret PF messages.

## State and Persistence Behavior
It owns no storage. The constants describe VF MMIO register state and exported functions mutate runtime `struct wx` state and hardware registers.

## Dependencies and Integration Points
It assumes `struct wx`, `struct net_device`, and kernel integer/bitfield macros are available. It is included by VF low-level code, VF common lifecycle code, VF queue configuration code, and concrete VF modules.

## Risks and Edge Cases
Encoding helpers convert descriptor counts and buffer sizes into hardware fields; incorrect counts or unsupported values can produce zero encodings. Constants cap VF queues at four TX/RX queues, while some concrete VFs choose lower limits. Register comments and array ranges must match silicon.

## Test Signals
Compile VF drivers, run VF reset/open with queue counts at boundaries, verify RSS key/RETA programming uses `WX_VXMRQC` correctly, and validate interrupt vector mapping and ITR writes for MSI-X VF configurations.
