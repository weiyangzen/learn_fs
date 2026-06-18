## sources/distributed-fs/lizardfs/src/mount/polonaise/options.h

Purpose: declares `parse_command_line` for the Polonaise server.

Important APIs: `parse_command_line(int argc, char **argv, Setup &setup)` mutates the caller-provided setup object and may exit the process on help or parse failure.

Integration: included by `main.cc`; depends on `Setup` from `setup.h`.

Risks and tests: process-exiting behavior complicates unit testing and embedding. Tests should isolate parse paths in a subprocess or refactor toward status-returning parsing.
