# sources/distributed-fs/ceph-client/drivers/firmware/turris-mox-rwtm.c

## Purpose
`turris-mox-rwtm.c` is the platform firmware driver for the Turris MOX rWTM firmware mailbox. It exposes board manufacturing data through sysfs, registers a hardware RNG backed by firmware random generation, and optionally registers a Turris signing key that delegates ECDSA signing to firmware.

## Important APIs, types, and functions
`struct mox_rwtm` contains the mailbox client/channel, HWRNG descriptor, last reply, coherent 4 KiB DMA buffer and physical address, command mutex, completion, board info fields, MAC addresses, and optional public key. The mailbox command set includes random, board info, ECDSA public key, hash/sign/verify, and OTP operations. `mox_get_status()` validates that a reply matches the requested command and maps firmware status encodings to Linux errno values.

`mox_rwtm_exec()` is the common command executor. It fills the command id, sends a mailbox message, waits either interruptibly or with a half-second timeout, then decodes the reply. `mox_rwtm_rx_callback()` stores the reply and completes the command if one is pending. `mox_get_board_info()` reads serial, board version, RAM size, and two MAC addresses. `mox_hwrng_read()` serializes access with `busy`, requests random bytes into the DMA buffer, copies up to 4 KiB out, and supports nonblocking `-EBUSY` behavior.

When `CONFIG_TURRIS_MOX_RWTM_KEYCTL` is enabled, helpers convert firmware's 521-bit ECC number format to binary, read the board public key, create a `turris_signing_key` subtype, and implement `mox_rwtm_sign()` by placing a SHA-512 digest and signature output slots into the DMA buffer for firmware signing.

## Control flow and integration
Probe allocates private state and a coherent DMA buffer, initializes the mutex and completion, requests mailbox channel 0, registers a devm action to free it, reads board info, optionally registers the signing key, verifies random-generation support, registers the HWRNG, and creates `/sys/firmware/turris-mox-rwtm` as an ABI compatibility symlink. The device exposes read-only attributes for serial number, board version, RAM size, and MAC addresses via `dev_groups`; attributes return `-ENODATA` when board info was not burned.

## State and persistence behavior
The driver caches board info and public key in RAM after probe. The coherent DMA buffer is reused for random and signing commands and protected by the `busy` mutex for command paths that share it. Firmware owns persistent manufacturing data, OTP state, random generation, and private key material. The sysfs compatibility symlink is removed through a devm cleanup action.

## Dependencies and integration points
Dependencies include the Armada 37xx rWTM mailbox message ABI, mailbox framework, DMA coherent allocation, HWRNG framework, sysfs/firmware kobject, Ethernet address formatting, SHA-512 constants, and optional keyctl/Turris signing key support. Device matching supports both `cznic,turris-mox-rwtm` and `marvell,armada-3700-rwtm-firmware`.

## Risks and test signals
Risks include stale completions because `mox_rwtm_exec()` does not reinitialize `cmd_done` in the function body, command/reply mismatch handling, DMA buffer bounds, firmware errno mapping, and concurrent command users sharing one reply buffer. Signing paths are sensitive to endian conversion and 521-bit number offsets. Test signals include successful probe, board info sysfs reads, HWRNG registration and reads under blocking/nonblocking modes, unsupported-command handling, signing key creation on keyed boards, and mailbox timeout/error injection.
