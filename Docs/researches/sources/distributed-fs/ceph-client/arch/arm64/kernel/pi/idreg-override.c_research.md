# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/idreg-override.c

Purpose: Parses very early command-line CPU feature overrides into global `arm64_ftr_override` structures before normal kernel mapping and cpufeature finalization.

Important types and APIs: `struct ftr_set_desc` describes ID registers, fields, shifts, widths, and optional filters. Descriptors cover MMFR0/1/2, PFR0/1, ISAR1/2, SMFR0, and software features. `init_feature_override()` clears overrides, stores boot status, parses bootargs and built-in cmdline, and cleans override cache lines. It also provides PI `skip_spaces()`.

Control flow: parser tokenizes cmdline words, normalizes dashes to underscores, matches `<reg>.<field>=<hex digit>`, applies filters, updates override val/mask, and recursively expands aliases such as `arm64.nosve`, `arm64.nomte`, `kvm_arm.mode=protected`, `nokaslr`, and `rodata=off`. Filters cascade dependent feature disables, for example clearing ZFR0 when SVE is disabled or SMFR0 when SME is disabled.

Dependencies and integration: runs from PI early mapping code with FDT bootargs. Depends on libfdt, cpufeature override globals exported to PI by linker aliases, boot EL status, cache maintenance, and no absolute-address constraints.

Risks and test signals: risks are parsing only one override per token, alias length truncation, filters silently masking user requests, stale cache-visible overrides before cpufeature reads, and VHE/nVHE override conflicts. Test boot parameters for all aliases, CONFIG_CMDLINE_FORCE precedence, FDT bootargs, protected/nVHE KVM modes, SVE/SME/MTE/PAuth disabling, and cache coherency on MMU-off boot.
