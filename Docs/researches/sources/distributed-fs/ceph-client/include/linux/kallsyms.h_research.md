# sources/distributed-fs/ceph-client/include/linux/kallsyms.h

## Purpose
Declares kernel symbol lookup and formatting helpers, with stubs when kallsyms is disabled. It also centralizes address classification for whether an address can be shown as a kernel symbol.

## Important APIs, Types, And Functions
Important constants are `KSYM_NAME_LEN` and `KSYM_SYMBOL_LEN`. Helpers include `is_kernel_text()`, `is_kernel()`, `is_ksym_addr()`, `dereference_symbol_descriptor()`, and `print_ip_sym()`. With `CONFIG_KALLSYMS`, APIs include `kallsyms_lookup_name()`, `kallsyms_lookup()`, `kallsyms_lookup_size_offset()`, symbol iteration, `sprint_symbol*()`, backtrace formatting, and `lookup_symbol_name()`.

## Control Flow
Address classification checks core kernel ranges and gate areas, optionally including all kernel addresses when `CONFIG_KALLSYMS_ALL` is set. Function descriptor architectures dereference kernel or module descriptors under RCU. Disabled kallsyms builds return null, zero, or `-EOPNOTSUPP`/`-ERANGE` stubs.

## State And Persistence
Symbol tables are generated at build/load time and live in kernel/module memory. The header itself stores no state. Visibility of raw values is controlled by `kallsyms_show_value()`.

## Dependencies And Integration Points
Depends on build IDs, modules, MM helpers, section boundaries, RCU guards, and printk formatting. Integrates with stack traces, live debugging, module diagnostics, tracing, and security policy around symbol exposure.

## Risks
Symbol value exposure can weaken KASLR, so permission checks matter. Buffer sizing must respect `KSYM_SYMBOL_LEN`. Descriptor dereferencing must handle modules that may unload, which is why RCU is used.

## Test Signals
Tests include enabled and disabled kallsyms builds, lookup by name/address, module symbol formatting with build IDs, permission checks for value display, function descriptor architectures, and `%pS`/backtrace output sanity.
