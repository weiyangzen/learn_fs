# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_stm32g0.c

## Purpose

`ucsi_stm32g0.c` drives STMicroelectronics STM32G0 Type-C PD controllers over I2C. It exposes the controller as a UCSI device and optionally updates or restores controller firmware through the STM32 I2C bootloader.

## Important APIs, Types, and Functions

`struct ucsi_stm32g0` stores the normal I2C client, optional bootloader dummy client, bootloader state, firmware name, UCSI object, and suspend wakeup flags. Bootloader helpers implement ACK checking, command framing, address transfer, mass erase, flash read/write, and bootloader version probing. UCSI callbacks perform register-addressed I2C reads and write the `UCSI_CONTROL` register. `ucsi_stm32g0_fw_cb()` is the asynchronous firmware callback that compares embedded firmware metadata, switches to bootloader, erases, writes flash in 256-byte chunks, sets option bytes to boot main flash, and registers UCSI.

## Control Flow

Probe creates the UCSI object, checks for an optional `firmware-name`, creates the bootloader-address dummy client when needed, and first probes the normal UCSI version. If normal UCSI is unavailable and firmware is configured, it probes bootloader version and marks `in_bootloader`. Non-bootloader devices request the alert IRQ and register UCSI immediately. Firmware loading runs asynchronously to avoid blocking boot. IRQ handling reads CCI and calls `ucsi_notify_common()`.

## State and Persistence Behavior

Runtime state tracks whether the controller is in bootloader mode and whether suspend saw a wake event. The firmware-update path persists new controller firmware and option bytes in STM32 flash; normal UCSI operation has no file-backed persistence.

## Dependencies and Integration Points

The driver depends on I2C transfers, threaded IRQs, Linux firmware loading, device properties, UCSI core, PM sleep callbacks, and STM32 bootloader protocol constants from AN2606/AN4221 behavior.

## Risks and Test Signals

Risks include interrupted firmware flashing, malformed firmware footer keyword/version, bootloader ACK/NACK/BUSY handling, endian/alignment assumptions in option-byte access, IRQs during suspend, and cleanup when firmware request fails after UCSI registration. Test signals include normal UCSI probe, bootloader-only recovery, firmware no-op when versions match, mass-erase/write failure paths, IRQ CCI notification, suspend wake IRQ accounting, and remove behavior in both bootloader and normal states.
