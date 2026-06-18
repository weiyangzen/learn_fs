# sources/distributed-fs/ceph-client/fs/nls/Makefile

## Purpose
This Makefile maps `CONFIG_NLS*` Kconfig symbols to the native language support object files compiled into the kernel or as modules.

## Important APIs, Types, And Functions
The build API is the kernel `obj-$(CONFIG_SYMBOL) += object.o` pattern. `CONFIG_NLS` builds `nls_base.o`. Codepage, ISO-8859, KOI8, UTF-8, Mac, and UCS2 utility symbols each add their corresponding table implementation. Some symbols build multiple objects, such as CP932 adding both `nls_cp932.o` and `nls_euc-jp.o`, and KOI8-U adding `nls_koi8-u.o` and `nls_koi8-ru.o`.

## Control Flow
There is no runtime control flow. Kbuild expands selected symbols into object lists. If a symbol is `m`, the object becomes a module; if `y`, it is linked built-in.

## State, Persistence, And Dependencies
State comes from the generated kernel configuration. The Makefile assumes each listed `.o` has a matching source file in `fs/nls` and that Kconfig exposes or selects the symbol.

## Integration Points
This file is the bridge between `fs/nls/Kconfig` and concrete charset modules such as `mac-celtic.o`, `mac-centeuro.o`, `mac-croatian.o`, `mac-cyrillic.o`, and `mac-gaelic.o`. Filesystem runtime charset lookup depends on the selected objects registering their `struct nls_table`.

## Risks
Symbol/object drift causes build failures or missing charset modules. The entries use a mix of tabs and spaces around `+=`, which is harmless for make but can make style checks noisy. Multi-object mappings must remain intentional because disabling one symbol can remove more than one charset table.

## Test Signals
Build all NLS symbols as modules and built-ins, run `make M=fs/nls`, verify expected `.ko` names, and mount a filesystem with each configured charset string to confirm lookup registration.
