# sources/control-plane/csi-lib-utils/release-tools/boilerplate/boilerplate.py

## Purpose

`boilerplate.py` checks source files for Kubernetes copyright/license boilerplate headers. It can scan a supplied file list or walk a root directory, compare each supported file type against `boilerplate.*.txt` references, and print files that fail.

## Important APIs and Flow

The script parses `--rootdir`, `--boilerplate-dir`, `--verbose`, and optional filenames. `get_refs` loads boilerplate templates keyed by extension or basename. `get_files` walks the tree, prunes ignored directories, filters files by template keys, and returns candidates. `file_passes` opens each file, chooses the matching reference, strips Go build tags and script shebangs, normalizes the first copyright year to `YEAR`, and compares only the header-length prefix. `main` prints failing filenames and exits `0`; callers decide whether non-empty output is an error.

## State, Dependencies, and Integration

State is in local template files and transient scan results. Dependencies are Python standard library modules: argparse, difflib, glob, os, re, sys, and date. `verify-boilerplate.sh` wraps this script and treats printed filenames as a failing verification signal.

## Risks and Test Signals

The script assumes all scanned extensions have a loaded reference and can raise a `KeyError` if filtering and template keys diverge. It ignores many vendored/generated paths by substring, which can skip unexpected paths with matching names. Its year regex only allows years from 2014 through the current date. Test coverage is indirect through `verify-boilerplate.sh` and Prow.
