# sources/cloud-native/composefs/man/meson.build

## Purpose
This Meson file generates and installs man pages from Markdown sources using `go-md2man`.

## Important APIs, Types, And Functions
The `manuals` dictionary maps man sections to page base names. A nested `foreach` creates one `custom_target` per page with `go-md2man -in @INPUT@ -out @OUTPUT@`, installing into `mandir/man<section>`.

## Control Flow
The top-level build enters this subdir only when `go-md2man` is found according to the `man` feature option.

## State And Persistence
Generated man page files are build artifacts and install artifacts.

## Dependencies And Integration Points
Depends on the top-level `go_md2man` program variable and Meson install directories. Covers `mkcomposefs`, `composefs-info`, `composefs-dump`, and `mount.composefs`.

## Risks
Missing Markdown source files or a missing converter prevents man generation when the feature is required. Page lists must stay synchronized with tool names.

## Test Signals
No direct tests in this subset. Build success with `-Dman=enabled` validates the generation path.
