# sources/cloud-native/ostree/src/libostree/ostree-lzma-decompressor.h

## Purpose
This private header declares the `OstreeLzmaDecompressor` GType and constructor.

## Important APIs, State, and Integration
It defines GObject type macros, forward declares the instance/class, declares `_ostree_lzma_decompressor_get_type()`, and exposes `_ostree_lzma_decompressor_new()`. The class derives from `GObject`; the implementation supplies the `GConverter` interface.

## Dependencies, Risks, and Tests
The header depends on GIO. It integrates with GLib converter streams used by object and archive readers. Risks are low at the declaration layer, but ABI/type macro correctness matters for casts and introspection-like internal use. Tests should ensure type registration, constructor success, and converter interface availability.
