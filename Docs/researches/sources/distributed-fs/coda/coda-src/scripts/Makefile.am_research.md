# sources/distributed-fs/coda/coda-src/scripts/Makefile.am

Purpose: Automake manifest for installing Coda client/server helper scripts and manpages.

Important declarations: `sbin_SCRIPTS` receives generated scripts such as `coda-client-setup`, `bldvldb.sh`, `createvol_rep`, `purgevol_rep`, `startserver`, `vice-setup`, and `vice-setup-rvm` under conditional `BUILD_CLIENT`/`BUILD_SERVER`. `dist_sbin_SCRIPTS` ships static helper scripts including `codastart`, log rotation, partial reinit, kill volumes, and setup substeps. `dist_man_MANS` lists corresponding manual pages. `EXTRA_DIST` distributes noninstalled utilities (`findparents.sh`, `volinfo.pl`, `volsizes.pl`, `pwdtopdbtool.py`). `CLEANFILES` removes generated script outputs.

Control flow/state: no runtime behavior. Build-time state is Automake's generated `Makefile.in` and configure substitution for `.in` scripts.

Dependencies/integration: integrates with top-level configure conditionals and install targets. Risks are missing helper scripts when conditionals do not match package composition, stale generated scripts in `CLEANFILES`, and static utilities distributed but not installed. Test signals are `make distcheck`, correct install contents under client-only/server-only builds, and generated scripts containing substituted paths.
