# sources/distributed-fs/coda/coda-src/dir/dirtest.c

## Purpose
Interactive and scriptable test harness for RVM-backed Coda directory operations.

## APIs, Types, and Functions
Registers parser commands for `init`, `ok`, `mdir`, `free`, `bulk`, `create`, `list`, `vdir`, `rdsfree`, `delete`, `empty`, `length`, `compare`, `convert`, `lookup`, `fidlookup`, `hash`, `printchain`, and `quit`. Uses `DH_*`, `DIR_*`, FID helpers, RVM/RDS initialization, and parser APIs.

## Control Flow, State, and Persistence
`main()` validates log/data files, initializes LWP and per-thread RVM data, loads an RDS heap into global `dd`, selects RVM directory mode, and enters an interactive parser or executes commands from a file. Commands begin/end RVM transactions around mutations, operate on up to 100 `DirHandle` slots, and print diagnostics. `dt_bulktest()` repeatedly creates/deletes directories and RVM allocations to stress allocation/free behavior.

## Dependencies and Integration
Depends on RVM/RDS, LWP, parser utilities, and the directory library. It provides manual regression coverage for directory body, handle, conversion, and transaction behavior.

## Risks and Test Signals
Risks include old command parser assumptions, several rough edges in argument strings, possible bad pointer/free behavior in `dt_free all`, and dependence on external RVM log/data setup. Test signals include `ok`/`DIR_DirOK`, create/delete lookup results, converted directory parsing through `vdir`, bulk stress completion, and transaction end status.
