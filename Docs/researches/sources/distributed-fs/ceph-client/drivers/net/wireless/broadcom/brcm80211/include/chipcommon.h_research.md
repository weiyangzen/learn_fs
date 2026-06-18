# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/chipcommon.h

Purpose: Defines the Broadcom chipcommon MMIO register layout and chipcommon/PMU capability bitfields.

Important APIs/types: `CHIPCREGOFFS(field)` computes register offsets in `struct chipcregs`. The struct maps chip ID/capabilities, OTP, interrupts, GPIO, watchdog, clocks, PLL delays, backplane access, flash/extbus, ECI, SROM, UARTs, save/restore, PMU registers, and SROM/OTP storage. Defines chipid masks, capability masks, PMU capability masks, save/restore control bits, retention bits, and `PMU_MAX_TRANSITION_DLY`.

Control flow and state: No executable flow. This file is the register ABI for MMIO access; state is hardware-resident in chipcommon registers.

Dependencies and integration: Includes `defs.h` for unique padding names. Used by PMU code, chip/AI utilities, GPIO/clock/SROM logic, and BCMA register access. Risks are severe if layout offsets drift, because wrong MMIO offsets can corrupt hardware state. Padding macro correctness, corerev-specific fields, and endian/MMIO access discipline are critical. Test signals include offset assertions, chip bring-up, PMU measurement, GPIO/clock operations, SROM reads, and hardware smoke tests across chipcommon revisions.
