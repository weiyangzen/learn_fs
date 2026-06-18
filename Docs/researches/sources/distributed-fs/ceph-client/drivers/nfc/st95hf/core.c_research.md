# sources/distributed-fs/ceph-client/drivers/nfc/st95hf/core.c

## Purpose

This file is the core Linux NFC digital-layer driver for the STMicroelectronics ST95HF NFC transceiver. It binds as an SPI driver, powers and resets the chip, registers an `nfc_digital_dev`, and implements initiator-side NFC operations for ISO14443A, ISO14443B, and ISO15693. It delegates raw SPI transfer details to `st95hf/spi.c` while keeping all NFC protocol selection, frame handling, WTX handling, IRQ completion, and lifecycle coordination in this file.

## Important APIs, types, and functions

The central state object is `struct st95hf_context`, which contains the SPI transport context, NFC digital device pointers, enable GPIO, optional regulator, the current transmission flag, current RF protocol/technology, RATS/WTX `fwi` timing state, and synchronization primitives. `struct cmd`, `struct param_list`, and `cmd_array[]` encode ST95HF commands such as echo, protocol select, register writes, WTX response, field-off, and ISO15693 select.

The internal command helper `st95hf_send_recv_cmd()` constructs ST95HF command packets from `cmd_array[]`, applies optional parameter substitutions, sends them over SPI, and optionally receives synchronous status responses. `st95hf_echo_command()`, `st95hf_send_spi_reset_sequence()`, and `st95hf_por_sequence()` implement bring-up and recovery. `st95hf_select_protocol()`, `secondary_configuration_type4a()`, `secondary_configuration_type4b()`, and `iso14443_config_fdt()` configure RF protocol and frame delay timing.

Digital-layer entry points are collected in `st95hf_nfc_digital_ops`: `st95hf_in_configure_hw()`, `st95hf_in_send_cmd()`, `st95hf_switch_rf()`, and a placeholder `st95hf_abort_cmd()`. Target-mode methods are stubs that return success without implementing peer-to-peer behavior. Driver binding is handled through `st95hf_probe()`, `st95hf_remove()`, `st95hf_id`, `st95hf_spi_of_match`, and `module_spi_driver()`.

## Control flow and state behavior

Probe allocates `st95hf_context`, stores the nested SPI context in device driver data, enables the optional `st95hfvin` regulator, initializes completions and locks, obtains the `enable` GPIO, installs a falling-edge threaded IRQ, performs a SPI reset sequence, runs POR via repeated echo checks, allocates an NFC digital device with ST95HF protocol masks, registers it, and initializes the semaphore/mutex used for asynchronous exchanges.

The normal initiator flow is `in_configure_hw()` selecting RF technology and framing, followed by `in_send_cmd()` wrapping the caller SKB with ST95HF command headers. For Type A frames it appends `sendrcv_trflag` and records whether the command is a RATS request. It allocates a receive SKB, stores the completion callback context, takes `exchange_lock`, and sends the SPI command as `ASYNC`; the IRQ thread later receives and completes the request.

The hard IRQ distinguishes synchronous internal command completion from asynchronous NFC exchange completion. If `spicontext.req_issync` is true it completes the SPI wait and returns. Otherwise the threaded handler reads the response, checks remove state under `rm_lock`, handles WTX requests in-line by changing frame delay timing and transmitting a WTX response, validates ST95HF and CRC error status, trims protocol-specific status/CRC bytes, restores default timing after WTX, then calls the digital-layer callback and releases `exchange_lock`.

Remove unregisters and frees the digital device under `rm_lock`, marks `nfcdev_free`, waits for the outstanding asynchronous exchange semaphore, sends a reset command, delays for reset completion, and disables the regulator. Persistent state is only in memory and in hardware registers; there is no filesystem persistence.

## Dependencies and integration points

This file depends on the Linux NFC digital framework (`net/nfc/digital.h`), SPI helper functions from `spi.h`, GPIO descriptors, regulators, IRQ threading, sk_buffs, and device tree compatible `st,st95hf`. The NFC subsystem calls the digital ops, while the SPI subsystem owns probe/remove. The chip-specific command constants and response interpretation tightly couple the file to ST95HF firmware behavior.

## Risks and edge cases

The asynchronous request lifecycle relies on `exchange_lock` being taken before a command and released exactly once from the IRQ thread; missed IRQs or SPI-send failures must release it correctly. The IRQ thread uses a static `wtx` flag, which is acceptable only if instances are effectively single-device or serialized; multiple devices could share that static state. `st95hf_abort_cmd()` is empty, so abort semantics depend on higher layers tolerating no immediate cancellation. Response trimming assumes minimum response sizes and protocol-specific layout, so malformed short responses risk invalid access unless lower transport/hardware prevents them. Probe initializes `rm_lock` after device registration, which means any immediate callback/IRQ path before initialization would be hazardous, although typical registration flow likely avoids it.

## Test signals

Useful validation includes module probe/remove with regulator and GPIO present, POR echo retry paths, synchronous protocol-select commands, each supported RF technology and framing, RATS response parsing with and without TA1/TB1, WTX request handling, CRC error propagation, timeout/error responses from ST95HF, and remove while an async exchange is pending. Hardware tests should watch SPI traffic, IRQ ordering, semaphore release, NFC polling behavior, and clean regulator/GPIO state after unload.
