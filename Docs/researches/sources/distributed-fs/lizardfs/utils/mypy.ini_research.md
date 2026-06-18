# sources/distributed-fs/lizardfs/utils/mypy.ini

Purpose: strict mypy configuration for Python utilities under this area, especially the Wireshark dissector generator.

Important settings: `disallow_untyped_defs = True` requires function annotations, `no_implicit_optional = True` keeps optional types explicit, `warn_return_any = True` surfaces imprecise return typing, and `warn_unused_configs = True` catches stale configuration.

Control flow/state: configuration-only; no runtime code or persistence.

Dependencies/integration: consumed by `mypy` when checking Python scripts. It applies a stricter policy than the legacy `make_dissector.py` style currently uses, so effective coverage depends on invocation scope and exclusions.

Risks and test signals: risk is drift between configured strictness and untyped historical scripts. Test signals are running `mypy` from this directory and confirming either intended failures or exclusions for generated/legacy scripts.
