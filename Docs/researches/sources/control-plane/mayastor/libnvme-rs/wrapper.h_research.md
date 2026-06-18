# sources/control-plane/mayastor/libnvme-rs/wrapper.h

Purpose: minimal C header used by bindgen to expose libnvme declarations.

Important APIs/types/functions: includes `<stddef.h>` and `<libnvme.h>`.

Control flow: no runtime behavior.

State/persistence: none; controls generated binding surface.

Dependencies/integration: consumed by `build.rs`; changes trigger Cargo rebuild through `rerun-if-changed`.

Risks: broad include exposes the full installed libnvme API, which may vary by distro/package version.

Test signals: binding generation and crate compilation fail quickly if the header or libnvme development package is missing.
