# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/migration/migration_test.go

Purpose: verifies 17-to-18 conversion semantics and the common migration framework integration.

Important APIs and control flow: table-driven tests use `common.RunMigrationTest` with assertions over `Provide`, deleted `Provider`/`Reprovider`, converted `"flat"` strategy, missing sections, empty sections, and unrelated section preservation. Reversibility and `Versions`/`Reversible` behavior are checked separately.

State and persistence: conversion tests are in-memory; reversibility test creates temp repo state through common helpers and backup files.

Dependencies and integration: exercises `mg17.NewMigration`, `BaseMigration`, and common testing helpers.

Risks and test signals: good signal for config field mapping. It does not test existing `Provide` merge conflicts, non-string strategy warning behavior, high worker count logging, or write failures.
