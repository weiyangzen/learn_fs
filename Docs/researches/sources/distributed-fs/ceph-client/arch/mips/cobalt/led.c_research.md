# sources/distributed-fs/ceph-client/arch/mips/cobalt/led.c

Purpose: registers the correct Cobalt LED platform device for Qube versus RaQ boards.

Important APIs: `cobalt_led_add()` checks `cobalt_board_id` and allocates `"cobalt-qube-leds"` for Qube1/Qube2 or `"cobalt-raq-leds"` otherwise. The resource is one MMIO byte at `0x1c000000`.

Control flow and state: board ID determines device name; registration failure releases the device. State persists only in the platform device.

Dependencies and integration: depends on `<cobalt.h>` board identification and matching LED drivers.

Risks and test signals: wrong board ID selects the wrong LED driver semantics. Boot should register one LED platform device; LED class entries should match board family.
