# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/__init__.py

## Role

Parser package initializer.

## Contents

Re-exports `gen_parser` from `._parser`.

## Dependencies

No parser construction happens here beyond importing the generator.

## Notable Behavior

This keeps `_main.py` imports simple: `from ._parser import gen_parser`.
