# sources/cloud-native/ostree/src/libostree/ostree-lzma-compressor.h

## Purpose
This private header declares the `OstreeLzmaCompressor` GType and constructor.

## Important APIs, State, and Integration
It defines the standard GObject type macros, forward declares the instance and class, declares `_ostree_lzma_compressor_get_type()`, and exposes `_ostree_lzma_compressor_new(GVariant *params)`. The class derives from `GObject`; the converter interface is attached in the implementation.

## Dependencies, Risks, and Tests
The header depends on GIO for converter/GObject declarations. It is used by code that wraps compression in `GConverterInputStream` or `GConverterOutputStream`. Risk is mostly API expectation drift around `params`, since construction accepts it but current implementation does not interpret it. Tests should verify type registration and constructor behavior.
