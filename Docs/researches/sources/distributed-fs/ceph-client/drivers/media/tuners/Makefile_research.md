# sources/distributed-fs/ceph-client/drivers/media/tuners/Makefile

Purpose: builds media tuner objects according to Kconfig symbols. It adds the DVB frontend include directory, defines composite objects for `tda18271`, and maps `CONFIG_MEDIA_TUNER_*` symbols to `.o` files.

Important integration points for this subset are `e4000.o`, `fc0011.o`, `fc0012.o`, `fc0013.o`, `fc2580.o`, `it913x.o`, `m88rs6000t.o`, `max2165.o`, and `mc44s803.o`. The file notes that entries should remain alphabetically sorted by Kconfig name, which helps reduce merge conflicts and makes symbol/object mismatches easier to audit.

There is no runtime state. Dependencies are the Kbuild system and Kconfig symbols. Risks: adding a tuner symbol without a matching object prevents code from building, and reordering against the documented sort convention increases maintenance friction. Test signals are kernel build coverage for each tuner as module/built-in and `scripts/checkkconfigsymbols.py`-style consistency checks.
