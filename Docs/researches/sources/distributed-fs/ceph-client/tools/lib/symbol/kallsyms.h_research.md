# sources/distributed-fs/ceph-client/tools/lib/symbol/kallsyms.h

Purpose: Public kallsyms parsing/classification API for tools symbol code.

Important APIs/types/functions: Defines default `KSYM_NAME_LEN` as 512. Inline `kallsyms2elf_binding()` maps `W` to `STB_WEAK`, uppercase types to `STB_GLOBAL`, and lowercase to `STB_LOCAL`. Declares `kallsyms2elf_type()`, `kallsyms__is_function()`, and `kallsyms__parse()`.

Control flow: Header provides binding classification inline and callback-driven parser declaration.

State and persistence: No state; parser callback decides storage.

Dependencies/integration: Includes `<elf.h>`, Linux ctype, and Linux types. Installed as `include/symbol/kallsyms.h`.

Risks: Binding/type mapping is intentionally coarse and may not reflect all kallsyms type letters. Callback signature must remain ABI-compatible for consumers.

Test signals: Compile and classify representative kallsyms type letters; parser behavior tested through `kallsyms.c`.
