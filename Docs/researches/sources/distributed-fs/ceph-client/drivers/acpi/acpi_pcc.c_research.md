# sources/distributed-fs/ceph-client/drivers/acpi/acpi_pcc.c

## Purpose
`acpi_pcc.c` installs an ACPI Platform Communications Channel address-space handler for PCC Operation Regions. It copies AML-provided buffers into PCC shared memory, sends mailbox commands, waits for interrupt completion, and copies results back.

## Important APIs, Types, And Functions
The main per-region type is `struct pcc_data`, containing a PCC mailbox channel, completion, mailbox client, and copied `struct acpi_pcc_info` context. Important functions are `pcc_rx_callback()`, `acpi_pcc_address_space_setup()`, `acpi_pcc_address_space_handler()`, and `acpi_init_pcc()`. `PCC_CMD_WAIT_RETRIES_NUM` scales timeout beyond the nominal channel latency.

## Control Flow
`acpi_init_pcc()` installs a handler for `ACPI_ADR_SPACE_PLATFORM_COMM` with `pcc_ctx` as handler context. Region setup allocates `pcc_data`, initializes the mailbox client and completion, copies PCC context fields, requests the PCC subspace channel, and requires interrupt-based transmit completion. Each AML access reinitializes completion, copies `ctx.length` bytes from the ACPI integer buffer into PCC shared memory, sends a mailbox message, waits up to `500 * latency`, marks txdone, copies shared memory back into the ACPI buffer, and returns ACPICA status.

## State And Persistence
Per-region `pcc_data` persists as ACPICA region context. PCC shared memory is external platform state. The file has no visible teardown for freeing region contexts.

## Dependencies And Integration Points
It depends on ACPICA address-space handling, `<acpi/pcc.h>`, PCC mailbox channels, Linux mailbox APIs, completions, and ACPI contexts prepared by the PCC table parser.

## Risks
`acpi_integer *value` is treated as a pointer to a buffer of `ctx.length`, which relies on ACPICA OpRegion plumbing and context correctness. Channels without interrupt txdone are rejected. Timeout sizing is arbitrary and can be too short or too long for specific platforms. Missing region-context cleanup could leak on dynamic region removal.

## Test Signals
Tests should cover handler install, missing PCC channel, non-interrupt channel rejection, successful command/response, timeout, mailbox send failure, and buffer length/context mismatches.
