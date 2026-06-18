# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-history.c

Purpose: this C example demonstrates the historical changelog API. It asks the user for start/end timestamps, requests history over a changelog directory, scans historical results, prints file names, and marks history changelogs done.

Important APIs: it calls `gf_changelog_init`, `gf_changelog_register`, `gf_history_changelog`, `gf_history_changelog_scan`, `gf_history_changelog_next_change`, and `gf_history_changelog_done`.

Control flow: after normal changelog registration, the program reads two integers with `scanf`, invokes `gf_history_changelog` with a hardcoded changelog directory and parallelism value `3`, then loops over historical scans until zero entries indicates completion.

State and persistence behavior: history APIs stage historical changelog files into library-managed directories and require `gf_history_changelog_done` after processing. `end_ts` reports the actual available end timestamp for the request.

Dependencies and integration points: includes `changelog.h` and links with `libgfchangelog`. It complements the live polling example by showing history recovery/backfill consumption.

Risks: the example uses `%d` printing for `unsigned long end_ts`, scans user input without validation, has hardcoded paths, and leaves some error handling commented. It is illustrative rather than production-safe.

Test signals: compile with pkg-config, run with a populated `.glusterfs/changelogs` directory, request valid and invalid timestamp ranges, confirm actual end timestamp behavior, and verify history done moves or cleans staged files.
