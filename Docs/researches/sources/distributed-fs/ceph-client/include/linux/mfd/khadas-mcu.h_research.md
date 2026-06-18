# sources/distributed-fs/ceph-client/include/linux/mfd/khadas-mcu.h

Purpose: This header maps the Khadas system-control MCU register space and parent state. It covers vendor/user passwords, MAC/USID/version/device identifiers, boot and wake controls, LEDs, shutdown, IR, USB/PCIe switching, user data, power-off and password commands, WOL/fan commands, and board IDs.

Important APIs, types, and constants: Register macros define read-only identity fields, read/write boot/wakeup/LED/shutdown/MAC/IR/sleep/switch/password/user-data registers, write-only command registers, and read-only shutdown status. The enum identifies VIM1, VIM2, VIM3, Edge, and Edge-V board IDs. `struct khadas_mcu` stores device and regmap pointers.

Control flow, state, and persistence: Consumers read identity/version data, configure wake sources and boot modes, update LED or fan controls, issue power-off/password/WOL commands, and access user data through regmap. Persistent state includes MCU NVM/user data, passwords, MAC address, wake policy, and boot settings.

Dependencies and integration points: It integrates with regmap-backed I2C MCU access, poweroff/reboot handlers, NVMEM/MAC providers, LED drivers, fan/hwmon support, wakeup sources, and board-detection code.

Risks and test signals: Risks include writing command-only registers accidentally, exposing or corrupting password/user-data fields, wrong board ID mapping, and wake-source settings persisting unexpectedly. Test signals include identity readback, boot/wake setting round trips, poweroff command path, LED/fan command tests, MAC/NVMEM reads, and suspend wakeup validation.
