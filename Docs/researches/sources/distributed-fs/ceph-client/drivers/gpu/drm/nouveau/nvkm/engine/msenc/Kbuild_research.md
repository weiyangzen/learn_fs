
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msenc/Kbuild

Purpose: placeholder build manifest for MSENC support.

Important APIs/types/functions: contains only the SPDX line and a commented-out `nvkm-y += nvkm/engine/msenc/base.o` entry, so no MSENC object is built from this directory.

Control flow/state: no runtime behavior.

Dependencies/integration: Kbuild-level integration only. Risk is intentional absence being mistaken for enabled support; uncommenting without implementation would affect build/link. Test signal is build output confirming no MSENC object from this file.
