<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/bases/config.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/scorecard/bases/config.yaml

## Purpose
Base Operator SDK scorecard configuration.

## Important APIs, Types, And Functions
Defines scorecard.operatorframework.io/v1alpha3 Configuration with one parallel stage and an initially empty tests list.

## Control Flow
Scorecard kustomization patches tests into `/stages/0/tests`.

## State And Persistence
No runtime state; rendered into bundle test config.

## Dependencies And Integration Points
Patched by basic and OLM scorecard patch files.

## Risks And Edge Cases
If patches fail, scorecard runs no tests despite a valid base config.

## Test Signals
The file exists solely to configure scorecard tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/bases/config.yaml -->
