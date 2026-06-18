<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init.h -->
# sources/distributed-fs/ceph-client/include/linux/init.h

Purpose: Core initialization annotation and initcall registration interface for built-in kernel code and modules.

Important APIs/types/functions: Section macros mark init/exit/ref/meminit code and data. `initcall_t`, `exitcall_t`, `initcall_entry_t`, initcall boundary symbols, boot command-line globals, architecture init prototypes, and `THIS_MODULE` are declared. Macros register early, pure, core, postcore, arch, subsys, fs, rootfs, device, late, sync, console, and exit calls. `struct obs_kernel_param`, `__setup()`, `early_param()`, and `early_param_on_off()` register boot parameter parsers.

Control flow: Linker collects initcall and setup entries; boot code parses early/setup params and runs initcall levels in order, freeing init sections later.

State/persistence: Init/exit section data may be discarded; boot command lines and setup tables persist through initialization. Module builds elide built-in setup macros.

Dependencies/integration: Integrates compiler attributes, linker scripts, LTO, PREL32 relocations, module ownership, and init/main.c.

Risks: Section mismatch annotations can hide real lifetime bugs; initcall ordering is link-order sensitive except special LTO handling.

Test signals: Build-time modpost section checks, boot initcall ordering, early parameter parsing, module versus builtin builds, and LTO/PREL32 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init.h -->
