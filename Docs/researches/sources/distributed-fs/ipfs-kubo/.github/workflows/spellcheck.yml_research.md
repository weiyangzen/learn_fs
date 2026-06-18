# sources/distributed-fs/ipfs-kubo/.github/workflows/spellcheck.yml

## Purpose
This workflow delegates repository spell checking to a unified reusable workflow.

## Important APIs, Types, And Functions
It grants read-only contents access and runs `ipdxco/unified-github-workflows/.github/workflows/reusable-spellcheck.yml@v1`.

## Control Flow
It runs on pull requests, master pushes, and manual dispatch. All spellcheck implementation details live in the reusable workflow.

## State And Persistence Behavior
The workflow is read-only with respect to repository contents.

## Dependencies And Integration Points
It depends on the external unified workflow and whatever spelling dictionaries/configuration that workflow expects from this repository.

## Risks And Test Signals
Risks are external workflow drift and false positives from project-specific vocabulary. The signal is the reusable spellcheck job status.
