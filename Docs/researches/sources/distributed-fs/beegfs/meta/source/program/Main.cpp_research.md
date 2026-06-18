## sources/distributed-fs/beegfs/meta/source/program/Main.cpp

Purpose: process entry point for the BeeGFS metadata server binary. It delegates all startup and shutdown behavior to `Program::main`.

Important APIs/functions: the only function is `int main(int argc, char** argv)`, returning `Program::main(argc, argv)`.

Control flow: no local initialization occurs before delegation, so all runtime checks and `App` lifecycle work are in `Program.cpp`.

State and persistence behavior: no state or persistence is touched in this file.

Dependencies and integration points: includes `Program.h`, making `Program` the bootstrap facade for the executable.

Risks: minimal. Any crash or failure behavior is controlled by `Program::main` and `App`.

Test signals: a smoke/link test should ensure the metadata-server target links exactly one `main` and returns the `Program::main` result.
