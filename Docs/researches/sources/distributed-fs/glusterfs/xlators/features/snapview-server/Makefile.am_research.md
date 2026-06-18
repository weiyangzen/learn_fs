# sources/distributed-fs/glusterfs/xlators/features/snapview-server/Makefile.am

Purpose: top-level Automake file for the snapview-server feature translator.

Important declarations: `SUBDIRS = src` recurses into the implementation directory.

Control flow/state: no runtime behavior or persistence.

Dependencies/integration: connects snapview-server to the parent feature-xlator build.

Risks/test signals: low risk; recursive build and distribution checks should ensure `src` is included.
