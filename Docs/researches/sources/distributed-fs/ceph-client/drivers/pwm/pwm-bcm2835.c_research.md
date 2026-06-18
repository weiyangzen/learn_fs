# sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm2835.c

Purpose: implements the two-channel BCM2835/Raspberry Pi PWM controller.

Important APIs/types/functions: `struct bcm2835_pwm` stores MMIO base, clock, and exclusive clock rate. `bcm2835_pwm_apply()` validates period bounds, converts period and duty to clock cycles, writes range/data registers, and updates per-channel control bits for mode, polarity, and enable. PM callbacks disable and reenable the clock.

Control flow: probe maps MMIO, enables the clock, gets an exclusive rate, stores the rate, marks the chip atomic, and registers two PWMs. Apply computes a maximum safe period to avoid 32-bit count overflow, rejects periods below two cycles, writes period and duty, then rewrites the control byte for the selected channel.

State and persistence: software state is clock rate and MMIO base. Hardware registers store current output; no `get_state` callback is implemented, so framework state is request-based after registration.

Dependencies and integration: depends on MMIO, common clock exclusive-rate API, OF compatible `brcm,bcm2835-pwm`, PM sleep ops, and the PWM core.

Risks and test signals: no readback means bootloader-initialized state is not imported. Applying one channel rewrites the shared control register and must preserve the other channel's byte. Test signals include both channels independently, period overflow limit, too-small period rejection, polarity bit behavior, suspend/resume clock restoration, and atomic apply assumptions.
