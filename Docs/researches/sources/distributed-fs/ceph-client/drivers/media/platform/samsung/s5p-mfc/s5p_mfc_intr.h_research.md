# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_intr.h

Purpose: declares the MFC interrupt wait and interrupt-flag cleanup helpers.

Important APIs and types: exports `s5p_mfc_wait_for_done_ctx`, `s5p_mfc_wait_for_done_dev`, `s5p_mfc_clean_ctx_int_flags`, and `s5p_mfc_clean_dev_int_flags`. It includes `s5p_mfc_common.h` so context and device structures are available.

Control flow: command issuers include this header, clear interrupt flags, issue a hardware/firmware command, then call the appropriate wait helper for the expected return command.

State and persistence: the header has no storage. Declared helpers mutate only transient `int_*` fields on MFC device/context structures.

Dependencies and integration points: integrates command, operation, stream, and control paths with the MFC interrupt handler through common interrupt state and wait queues.

Risks: the API returns only success or generic failure, so richer error handling requires inspecting other context/device fields. The `interrupt` boolean on the context wait is easy to misuse because it changes signal handling.

Test signals: compile coverage from all MFC command paths; runtime command-completion tests; and static checks that callers clean flags before waiting.
