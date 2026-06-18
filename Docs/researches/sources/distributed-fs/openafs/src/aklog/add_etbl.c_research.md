# sources/distributed-fs/openafs/src/aklog/add_etbl.c

## Purpose

`add_etbl.c` is a small compatibility shim for platforms whose com_err implementation does not provide `add_to_error_table`. It adapts the older or alternate `add_error_table` API to the `add_to_error_table(struct et_list *)` interface expected by the surrounding aklog/Kerberos error-table code.

## Important APIs and control flow

The entire implementation is conditional on `#ifndef HAVE_ADD_TO_ERROR_TABLE`. When the platform already provides `add_to_error_table`, this translation unit effectively contributes no symbols. Otherwise it includes OpenAFS standard definitions, com_err declarations, and `afs/error_table.h`. If `HAVE_ADD_ERROR_TABLE` is also missing, it forward-declares `void add_error_table(const struct error_table *);`.

The implemented `add_to_error_table` accepts `struct et_list *new_table` and calls `add_error_table((struct error_table *) new_table->table)`. There is no validation, allocation, or error handling.

## State and persistence behavior

The function mutates whatever global error-table registry is managed by the linked com_err implementation through `add_error_table`. It has no file or durable state and no local static state.

## Dependencies and integration points

This file depends on configure-time feature detection for `HAVE_ADD_TO_ERROR_TABLE` and `HAVE_ADD_ERROR_TABLE`, the shape of `struct et_list`, and compatibility between `new_table->table` and `struct error_table`. It exists to keep aklog-related code building across com_err variants from Kerberos or system libraries.

## Risks and test signals

The cast from `new_table->table` to `struct error_table *` assumes ABI compatibility. If the com_err headers change the table representation, this shim could compile but register invalid data. The function also assumes `new_table` and `new_table->table` are non-null. Test signals are mostly build-matrix based: configure/build on platforms with native `add_to_error_table`, with only `add_error_table`, and with the shim declaration path. Runtime tests should trigger an aklog error path that requires registered error tables and confirm readable com_err messages.
