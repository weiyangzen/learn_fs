# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/Makefile.am

Purpose: top-level Automake file for the thin-arbiter feature translator.

Important declarations: recurses into `src` and defines an empty `CLEANFILES`.

Control flow/state: build traversal only; no runtime behavior.

Dependencies/integration: integrates thin-arbiter into the feature xlator build tree.

Risks/test signals: low risk. Build/distribution tests should confirm the `src` subdir is included and clean targets remain valid.
