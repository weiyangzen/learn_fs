# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/workarounds.c

Purpose: applies small BCM47xx board-specific hardware workarounds not represented as normal devices.

Important APIs and functions: `bcm47xx_workarounds_enable_usb_power()` requests a GPIO and drives it high for USB power. `bcm47xx_workarounds()` switches on detected board IDs and enables USB power GPIOs for known models.

Control flow: called from BCM47xx board setup after board detection. Only listed boards take action; others return immediately.

State and persistence: requests GPIO ownership and changes pin output state for the current boot only.

Dependencies and integration points: depends on `bcm47xx_board.board`, Linux GPIO request helpers, and the platform setup path.

Risks and test signals: wrong GPIO data can keep USB ports unpowered or conflict with another signal. Test by checking GPIO request success, USB VBUS availability, and device enumeration on affected boards.
