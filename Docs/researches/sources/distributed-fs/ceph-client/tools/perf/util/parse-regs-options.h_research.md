
# sources/distributed-fs/ceph-client/tools/perf/util/parse-regs-options.h

Purpose: declares parse-options callbacks for register sampling options.

Important APIs/types/functions: forward-declares `struct option` and exposes `parse_user_regs` plus `parse_intr_regs`.

Control flow: none; callbacks are implemented in `parse-regs-options.c`.

State and persistence: no state in the header.

Dependencies: parse-options users must include the actual `struct option` definition.

Integration points: perf record CLI option tables.

Risks: minimal; compile coverage verifies the callback signatures stay compatible with subcmd parse-options. Runtime tests should cover user and interrupt register options.
