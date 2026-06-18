# sources/distributed-fs/lustre-release/lnet/utils/lnet.pc.in

## Purpose
Pkg-config template for Lustre Network API/kAPI consumers.

## Important Fields
Defines install variables, `symversdir`, `Cflags`, `Libs`, `Description`, `Name`, and `Version`. Configure substitutes path and version placeholders.

## Control Flow
No runtime flow. The configured file is installed as `lnet.pc`.

## State And Persistence
Persists as installed build metadata for downstream users.

## Dependencies And Integration Points
Consumers use `pkg-config --cflags --libs lnet` or `pkg-config --variable=symversdir lnet`.

## Risks
The metadata `Name` is `lnet-kapi` while the pkg-config file is `lnet.pc`; scripts should use the installed package lookup correctly. Wrong substitutions break consumers.

## Test Signals
Run pkg-config after install and verify include flags, `-llnetconfig`, and `symversdir`.
