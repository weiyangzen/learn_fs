# sources/distributed-fs/openafs/src/bucoord/Makefile.in

This makefile builds the backup coordinator command (`backup`), support archive `libbxdb.a`, generated `bc.h`/`bucoord_errs.c`, installed `bucoord_prototypes.h`, and the `btest` helper. It wires bucoord against backup database, tape, volume, vldb, kauth, ubik, Rx, LWP, cmd, util, opr, and crypto libraries.

Important build variables are `LIBS`, `BACKSRCS`, `BACKOBJS`, generated-header dependencies, and targets `libbxdb.a`, `backup`, `btest`, `install`, `dest`, and `clean`. `bc.h` is generated from `bucoord_errs.et` plus `bc.p.h`; `bucoord_errs.c` comes from COMPILE_ET.

State is build-output state: generated error/header files, object files, archive, executable, component version source, and installed artifacts. Dependencies are top-level config, LWP config, COMPILE_ET, many OpenAFS libraries, and generated bubasics headers. Risks include library ordering sensitivity, broad transitive dependency surface, `CFLAGS_commands.o=@CFLAGS_NOERROR@` suppressing strict warnings for commands, legacy `dest` path, and generated `bc.h` staleness. Test signals are clean generated rebuild, link success for `backup` and `btest`, install layout, and downstream inclusion of `bc.h`.
