# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeinit.c

## Purpose
Initializes system GPE blocks from the FADT and updates GPE dispatch metadata when new tables introduce `_Lxx` or `_Exx` methods. It also decodes method names into GPE numbers, trigger types, and dispatch method associations.

## Important APIs, Types, And Functions
- `acpi_ev_gpe_initialize` creates optional FADT GPE0 and GPE1 blocks from FADT lengths/addresses and SCI interrupt routing.
- `acpi_ev_update_gpes` walks all GPE block devices after dynamic table load and enables newly discovered methods for a specific owner ID.
- `acpi_ev_match_gpe_method` is the namespace walk callback that recognizes `_Lxx`/`_Exx`, parses hex GPE numbers, validates block membership, detects handler conflicts, and records method dispatch data.

## Control Flow
Initialization locks the namespace, computes register counts as half of FADT GPE block lengths, creates GPE0 if present, then creates GPE1 if present and non-overlapping with GPE0. Missing blocks are valid. Dynamic update locks events, walks every xrupt and block, and searches each block's GPE device for methods owned by the newly loaded table. Method matching filters by owner when requested, requires names beginning with `_L` or `_E` plus two hex digits, ignores methods outside the block's GPE range, refuses to override installed handlers, reports `_Lxx`/`_Exx` trigger conflicts, disables the GPE, and sets dispatch flags plus method node.

## State And Persistence
State includes `acpi_gbl_gpe_fadt_blocks[0..1]`, FADT-derived register counts/base numbers, xrupt/block lists, per-event flags and method nodes, and update walk counters. This file no longer executes `_PRW`; wake GPE ownership is expected to be configured by the host OS.

## Dependencies And Integration Points
Depends on FADT global data, optional logical GPE block addresses, namespace and events mutexes, GPE block creation, method walking, GPE low-level lookup, hardware low-level GPE disable, and owner IDs assigned to loaded ACPI tables.

## Risks And Edge Cases
GPE0 and GPE1 overlap is detected and causes GPE1 to be ignored. Methods with malformed names are silently ignored with debug output. Existing handlers take precedence over methods. If both `_Lxx` and `_Exx` exist, the first wins and a mismatch error is logged. Dynamic updates must filter by table owner to avoid reprocessing unrelated methods.

## Test Signals
Test no-GPE FADT, GPE0-only, GPE1-only, overlapping GPE0/GPE1, logical versus physical addresses, valid `_Lxx` and `_Exx` registration, malformed method names, duplicate level/edge method conflicts, handler-over-method precedence, and dynamic `Load()` enabling newly introduced GPE methods.
