# sources/distributed-fs/ceph-client/tools/power/pm-graph/bootgraph.py

## Purpose
Implements BootGraph, a Python tool that captures or reprocesses Linux boot `dmesg` and optional function-graph ftrace logs, then emits an HTML boot timeline through shared `sleepgraph` library facilities.

## Important APIs, Types, and Functions
Important classes are `SystemValues` and `Data`. Major functions include `parseKernelLog`, `parseTraceLog`, `retrieveLogs`, `colorForName`, `cgOverview`, `createBootGraph`, `updateCron`, `updateGrub`, `updateKernelParams`, `doError`, and `printHelp`. The main block parses options for ftrace/callgraph, reboot automation, log replay, output, bootloader update, and utility commands.

## Control Flow, State, and Persistence
For a normal run it root-checks, optionally verifies ftrace, captures dmesg/ftrace into an output directory, parses initcall start/end messages into kernel/user phases, associates ftrace callgraphs with initcalls, generates timeline HTML/CSS/JS, stores hidden logs when requested, and writes result fields. Reboot mode mutates `/etc/default/grub`, runs grub update, installs an `@reboot` root cron entry, reboots, then cronjob mode restores cron/grub and disables tracing. Persistent effects can include output directories, result files, cron changes, grub changes, and ftrace state.

## Dependencies and Integration Points
Depends heavily on `sleepgraph.py` as `aslib`, Linux `/proc`, dmesg, debugfs/tracefs ftrace, grub tooling, crontab, root privileges, and standard Python modules. Installed by pm-graph Makefile as `bootgraph`.

## Risks and Test Signals
Bootloader/cron mutation is high risk and should be tested only in controlled environments. HTML generation embeds parsed names with limited escaping; dmesg log escaping omits semicolons. Parsing assumes initcall_debug log formats and stops after 120 seconds. Test replay mode with fixture dmesg/ftrace, no initcall data errors, manual reboot output, ftrace filter validation, grub restore paths, and output ownership under sudo.
