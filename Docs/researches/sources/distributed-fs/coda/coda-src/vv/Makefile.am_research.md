# sources/distributed-fs/coda/coda-src/vv/Makefile.am

## Purpose

This Automake fragment builds the Coda version-vector helper library as an uninstalled libtool archive.

## Important APIs, Types, and Functions

It declares `noinst_LTLIBRARIES = libvv.la` and sets `libvv_la_SOURCES` to `inconsist.cc`, `inconsist.h`, `nettohost.cc`, and `nettohost.h`. `AM_CPPFLAGS` adds RPC2 flags and include paths for base and vicedep headers.

## Control Flow

There is no runtime flow. During build generation, Automake emits rules to compile the listed sources into `libvv.la`.

## State and Persistence Behavior

It affects build artifacts only. No runtime persistence.

## Dependencies and Integration Points

The library is private to the build and depends on RPC2, `lib-src/base`, and generated/source vicedep headers for Coda types such as `ViceVersionVector`.

## Risks and Test Signals

Missing generated vicedep headers or RPC2 flags will break compilation. Tests are build-oriented: run autoreconf/configure/make for this directory and link a consumer of `libvv.la`.
