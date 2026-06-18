# sources/distributed-fs/ceph-client/scripts/gdb/linux/Makefile

Purpose: Builds/generated support for the Linux GDB Python helper package.

Important APIs/rules: In out-of-tree builds, creates symlinks for Python files from source to object directory. Generates `constants.py` from `constants.py.in` by preprocessing it as C, then deleting the C-header prelude through the marker. Cleans Python bytecode files.

Control flow: `always-y` includes symlinks when `building_out_of_srctree` and always includes `constants.py`. The generation rule uses `$(CPP) -E -x c -P $(c_flags)` then `sed -i`.

State/persistence: Produces symlinked helper files and generated `constants.py` in the object tree.

Dependencies/integration: Kbuild, CPP, sed, kernel include paths/config macros, and the Python helper package.

Risks: Generated constants depend on current kernel configuration and headers. Marker deletion must match `constants.py.in`. Out-of-tree symlink behavior depends on path correctness.

Test signals: In-tree and out-of-tree builds, changed config constants, absence of stale bytecode, and import of generated `linux.constants` in GDB.
